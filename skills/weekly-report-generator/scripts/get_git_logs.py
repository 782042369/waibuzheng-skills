#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git日志获取脚本

功能：
- 获取单个或多个项目的Git日志
- 按星期几分组（周一到周日）
- 支持调休补班情况（不过滤周末）
- 返回结构化JSON数据
- 添加输入验证和友好错误提示

作者：老王
日期：2026-01-15
"""

import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# 导入公共模块
try:
    from .common import (
        fix_windows_console_encoding,
        validate_date,
        validate_repo_path,
        get_week_day_name
    )
except ImportError:
    from common import (
        fix_windows_console_encoding,
        validate_date,
        validate_repo_path,
        get_week_day_name
    )

# 修复 Windows 控制台编码问题
fix_windows_console_encoding()


# ========== 常量定义 ==========

# 提交过滤关键词（按类型分组）
_SKIP_PATTERNS = {
    # 直接过滤（无长度限制）
    "always_skip": [
        "revert:", "回滚", "撤销", "rollback", "backout",  # 回滚
        "initial commit", "初始化", "init", "first commit",  # 初始化
        "empty commit", "空提交", "trigger build", "trigger ci",  # 空提交
        "no-op", "noop", ".", "trigger", "占位",  # 占位
        "bump version", "版本号", "version update",  # 版本号
        "update version", "bump.", "v1.", "v2.", "v3.",
        "wip", "work in progress", "tmp", "temp", "临时",  # WIP
        "test commit", "测试提交", "draft", "草稿",
        "tweak", "调整", "微调", "小改",
        # 新增：过滤无意义的分支和技术栈名称
        "add branch", "add develop", "add feature", "create branch",  # 添加分支
        "merge branch", "merge develop", "merge feature",  # 合并分支
        "update branch", "delete branch", "remove branch",  # 更新/删除分支
    ],
    # 单词提交（单独处理）
    "single_word_skip": [
        "backend", "frontend", "develop", "master", "main",  # 分支名
        "feature", "fix", "bug", "issue", "patch",  # 通用术语
        "config", "setting", "setup", "init",  # 配置
        "test", "tests", "spec", "mock",  # 测试
        "docs", "readme", "license", "changelog",  # 文档
        "update", "fix", "add", "remove", "delete",  # 通用动词
        "refactor", "optimize", "improve", "clean",  # 优化
        "tmp", "temp", "backup", "bak",  # 临时
    ],
    # 有长度限制的模式（pattern: max_length）
    "with_length_limit": {
        "format": (["format", "格式化", "lint", "prettier", "black",
                    "fmt", "代码格式", "formatting", "代码风格"], 25),
        "comment": (["comment", "注释", "comments only", "仅注释",
                     "update comment", "更新注释"], 25),
        "lock": (["package-lock", "yarn.lock", "go.sum", "cargo.lock",
                   "pom.xml", "gemfile.lock", "composer.lock",
                   "依赖更新", "update lock", "lock file", "锁文件"], 40),
        "cicd": (["workflow", ".github", ".gitlab", "actions", "ci:", "[ci]",
                  "cd:", "pipeline", ".gitlab-ci", "jenkins", "travis"], 30),
        "temp_file": ([".ds_store", "thumbs.db", ".gitignore", ".dockerignore",
                        ".env.example", "delete tmp", "删除临时文件"], 30),
        "trivial_fix": (["fix typo", "typo", "fix space", "fix newline",
                          "fix tab", "fix indent", "修复空格", "修复缩进"], 20),
        "delete": (["delete ", "删除", "remove ", "移除", "drop", "舍弃"], 25),
    },
    # 文档更新（特殊处理）
    "doc": ["update readme", "update changelog", "update license",
            "文档更新", "文档调整", "readme update", "changelog update",
            "update documentation", "update docs"]
}


# ========== 辅助函数 ==========

def _matches_any_pattern(text: str, patterns: List[str]) -> bool:
    """检查文本是否匹配任一模式"""
    return any(pattern in text for pattern in patterns)


def _should_skip_doc_update(message: str, message_length: int) -> bool:
    """
    判断是否应该过滤文档更新提交

    如果包含冒号，检查冒号后的内容长度
    否则检查总长度
    """
    if ':' in message:
        after_colon = message.split(':', 1)[1].strip()
        return len(after_colon) < 10
    return message_length <= 30


# ========== 输入验证辅助函数 ==========

def print_validation_error(errors: List[str]) -> None:
    """打印友好的验证错误消息"""
    print("\n❌ 输入验证失败！")
    print("请检查以下问题：\n")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")
    print("\n💡 提示：")
    print("  - 日期格式：YYYY-MM-DD（例如：2025-01-13）")
    print("  - 路径格式：绝对路径或相对路径均可")
    print("  - Git 仓库：必须包含 .git 目录")
    print()


def should_skip_commit(commit) -> bool:
    """
    判断是否应该跳过该提交（过滤无意义提交）

    过滤规则（见 _SKIP_PATTERNS 常量）：
    1. 合并提交（merge commit）
    2. 直接过滤（回滚、初始化、WIP等）
    3. 单词提交（backend、frontend、develop等）
    4. 有长度限制的模式（格式化、文档、CI/CD等）
    5. 文档更新（特殊处理：检查冒号后内容）
    6. 少于8个字符的极短提交（提高门槛）
    7. 只有标点符号的提交
    8. 空格或特殊字符过多的提交

    Args:
        commit: Git commit 对象

    Returns:
        True 表示跳过（无意义），False 表示保留（有意义）
    """
    message = commit.message.strip().lower()
    message_length = len(message)

    # 1. 过滤 merge commit
    if len(commit.parents) > 1:
        return True

    # 2. 直接过滤（无长度限制）
    if _matches_any_pattern(message, _SKIP_PATTERNS["always_skip"]):
        return True

    # 3. 单词提交检查（新增）
    # 检查是否是单个单词（不包含空格或只有少量空格）
    words = message.split()
    if len(words) <= 2:  # 1-2个单词
        # 检查是否匹配单次跳过列表
        if _matches_any_pattern(message, _SKIP_PATTERNS["single_word_skip"]):
            return True
        # 或者只是单个单词且长度很短（< 15字符）
        if len(words) == 1 and message_length < 15:
            return True

    # 4. 有长度限制的模式
    for category, (patterns, max_length) in _SKIP_PATTERNS["with_length_limit"].items():
        if _matches_any_pattern(message, patterns):
            if message_length <= max_length:
                return True

    # 5. 文档更新（特殊处理）
    if _matches_any_pattern(message, _SKIP_PATTERNS["doc"]):
        if _should_skip_doc_update(message, message_length):
            return True

    # 6. 少于8个字符的极短提交（提高门槛从5到8）
    if message_length < 8:
        return True

    # 7. 只有标点符号或特殊字符的提交
    if not message or all(char in '。，！？、.,;:!?\n\r\t ' for char in message):
        return True

    # 8. 空格或特殊字符过多的提交（新增）
    # 如果空格和标点占比超过50%，认为是无意义提交
    special_chars = sum(1 for char in message if char in ' ，。！？、.,;:!?\n\r\t')
    if special_chars > message_length * 0.5:
        return True

    return False


def get_git_logs(
    repo_path: str,
    start_date: str,
    end_date: str
) -> List[str]:
    """
    获取单个Git仓库的日志（精简模式）

    Args:
        repo_path: Git仓库路径
        start_date: 开始日期（YYYY-MM-DD格式）
        end_date: 结束日期（YYYY-MM-DD格式）

    Returns:
        提交消息列表（字符串数组）
    """
    try:
        import git
    except ImportError:
        print("错误：需要安装gitpython库")
        print("请运行：pip install gitpython")
        sys.exit(1)

    repo = Path(repo_path)

    # 检查是否是Git仓库
    if not (repo / ".git").exists():
        print(f"警告：{repo_path} 不是Git仓库，跳过")
        return []

    try:
        repo_obj = git.Repo(repo_path)
    except Exception as e:
        print(f"错误：无法打开Git仓库 {repo_path}: {e}")
        return []

    commits_data = []

    try:
        # 解析日期
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        # 结束日期加一天，包含当天的所有提交
        end_dt = end_dt + timedelta(days=1)

        # 获取提交记录
        for commit in repo_obj.iter_commits(
            since=start_dt,
            until=end_dt
        ):
            # 应用过滤逻辑（跳过无意义提交）
            if should_skip_commit(commit):
                continue

            # 只保留消息第一行（最简洁）
            commit_message = commit.message.strip().split('\n')[0]
            commits_data.append(commit_message)

    except Exception as e:
        print(f"错误：获取Git日志失败 {repo_path}: {e}")
        return []

    return commits_data


def group_by_weekday(commits: List[Dict]) -> Dict[str, List[Dict]]:
    """
    按星期几分组提交记录（支持周一到周日）

    Args:
        commits: 提交记录列表

    Returns:
        按星期几分组的字典（包含周一到周日）
    """
    grouped = {
        "周一": [],
        "周二": [],
        "周三": [],
        "周四": [],
        "周五": [],
        "周六": [],
        "周日": []
    }

    for commit in commits:
        # 兼容完整模式（weekday）和精简模式（wd）
        weekday = commit.get("weekday") or commit.get("wd")
        if weekday and weekday in grouped:
            grouped[weekday].append(commit)

    return grouped


def update_task_status(output_dir: str, week: int, status: str) -> None:
    """
    更新任务状态

    Args:
        output_dir: 输出目录
        week: 周数
        status: 状态 (pending/in_progress/completed/failed)
    """
    tasks_file = Path(output_dir) / "tasks.json"
    if not tasks_file.exists():
        print(f"警告：tasks.json 文件不存在，跳过状态更新")
        return

    try:
        with open(tasks_file, "r", encoding="utf-8") as f:
            tasks_data = json.load(f)

        # 更新指定周的状态
        for task in tasks_data.get("tasks", []):
            if task["week"] == week:
                task["status"] = status
                break

        # 写回文件
        with open(tasks_file, "w", encoding="utf-8") as f:
            json.dump(tasks_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 已更新第{week}周任务状态为：{status}")
    except Exception as e:
        print(f"警告：更新任务状态失败：{e}")


def split_by_week(commits: List[Dict], start_date: str, end_date: str, output_dir: str) -> int:
    """
    按周拆分提交记录，输出多个 JSON 文件

    Args:
        commits: 提交记录列表
        start_date: 开始日期（YYYY-MM-DD 格式）
        end_date: 结束日期（YYYY-MM-DD 格式）
        output_dir: 输出目录

    Returns:
        拆分的周数
    """
    # 解析日期
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    # 计算时间范围内的所有周
    # 找到 start_date 所在周的周一
    start_weekday = start_dt.weekday()  # 0=周一, 6=周日
    week_start = start_dt - timedelta(days=start_weekday)

    # 按周分组
    weeks = {}
    current_week_start = week_start
    week_num = 1

    while current_week_start <= end_dt:
        current_week_end = current_week_start + timedelta(days=6)

        # 筛选该周的提交
        week_commits = []
        for commit in commits:
            commit_date = datetime.strptime(commit["date"], "%Y-%m-%d")
            if current_week_start <= commit_date <= current_week_end:
                week_commits.append(commit)

        # 保存该周的数据
        week_data = {
            "week": week_num,
            "year": current_week_start.year,
            "start_date": current_week_start.strftime("%Y-%m-%d"),
            "end_date": current_week_end.strftime("%Y-%m-%d"),
            "commits": week_commits
        }

        # 输出到文件
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        week_file = output_path / f"weekly_data_{week_num:02d}.json"
        with open(week_file, "w", encoding="utf-8") as f:
            json.dump(week_data, f, ensure_ascii=False, indent=2)

        weeks[week_num] = week_file.name
        week_num += 1
        current_week_start = current_week_end + timedelta(days=1)

    # 生成任务清单
    tasks = {
        "total": len(weeks),
        "tasks": [
            {"week": w, "file": f, "status": "pending"}
            for w, f in weeks.items()
        ]
    }

    tasks_file = output_path / "tasks.json"
    with open(tasks_file, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

    return len(weeks)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="获取Git日志并按星期几分组（支持周一到周日）"
    )
    parser.add_argument(
        "--paths",
        type=str,
        required=True,
        help="项目路径列表，用逗号分隔（如：path1,path2,path3）"
    )
    parser.add_argument(
        "--since",
        type=str,
        required=True,
        help="开始日期（YYYY-MM-DD格式）"
    )
    parser.add_argument(
        "--until",
        type=str,
        required=True,
        help="结束日期（YYYY-MM-DD格式）"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="输出到文件（避免控制台编码问题）"
    )
    parser.add_argument(
        "--split-by-week",
        action="store_true",
        help="按周自动拆分数据，输出多个 weekly_data_XX.json 文件和 tasks.json"
    )

    args = parser.parse_args()

    print(f"正在获取 {args.since} 至 {args.until} 的 Git 日志...")

    # 解析并验证项目路径
    paths = [p.strip() for p in args.paths.split(",")]

    # 处理输出路径：自动添加 /tmp/ 子目录（如果父目录不是 tmp）
    if args.output:
        output_path = Path(args.output)
        # 检查父目录是否已经是 tmp
        if output_path.parent.name == "tmp":
            # 已经在 tmp 目录下，直接使用
            actual_output = output_path
        else:
            # 创建 tmp 子目录
            tmp_dir = output_path.parent / "tmp"
            tmp_dir.mkdir(parents=True, exist_ok=True)
            # 修改输出路径到 tmp 目录
            actual_output = tmp_dir / output_path.name
    else:
        actual_output = None

    # 输入验证
    errors = []

    # 验证日期
    for date_arg, date_label in [(args.since, "开始日期"), (args.until, "结束日期")]:
        is_valid, error = validate_date(date_arg)
        if not is_valid:
            errors.append(f"{date_label}：{error}")

    # 验证路径
    for path in paths:
        is_valid, error = validate_repo_path(path)
        if not is_valid:
            errors.append(error)

    if errors:
        print_validation_error(errors)
        sys.exit(1)

    # 获取所有项目的日志
    all_commits = []

    for i, path in enumerate(paths, 1):
        commits = get_git_logs(path, args.since, args.until)
        all_commits.extend(commits)

    # 构建结果（精简模式）
    result = {
        "total": len(all_commits),
        "messages": all_commits  # 直接是字符串数组
    }
    total_commits = len(all_commits)

    # 如果启用了按周拆分
    if args.split_by_week:
        if not actual_output:
            print("❌ 错误：--split-by-week 需要指定 --output 参数")
            sys.exit(1)

        # 提取输出目录（如果已经在 tmp 下，使用父目录）
        if actual_output.parent.name == "tmp":
            output_dir = str(actual_output.parent.parent)
        else:
            output_dir = str(actual_output.parent)

        # 按周拆分
        week_count = split_by_week(all_commits, args.since, args.until, output_dir)

        print(f"✅ 已按周拆分为 {week_count} 个文件：")
        print(f"   输出目录：{output_dir}")
        print(f"   文件格式：weekly_data_01.json ~ weekly_data_{week_count:02d}.json")
        print(f"   任务清单：tasks.json")
        print()
        print("🔄 拆分完成！现在开始处理每个周报：")

        return  # 拆分模式下不再输出单个文件

    # 输出JSON（到文件或控制台）
    json_output = json.dumps(result, ensure_ascii=False, indent=2)

    if actual_output:
        # 输出到文件（自动放到 tmp 目录），避免控制台编码问题
        with open(actual_output, "w", encoding="utf-8") as f:
            f.write(json_output)
        print(f"✅ 已保存 {total_commits} 条提交记录到：{actual_output}")
    else:
        # 输出到控制台
        print()
        print("-" * 60)
        print(json_output)
        print("-" * 60)


if __name__ == "__main__":
    main()
