#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git日志获取脚本

功能：
- 获取单个或多个项目的Git日志
- 按周一到周五分组
- 只返回工作日的提交
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


# ========== 输入验证函数（内联） ==========

def validate_date(date_str: str) -> Tuple[bool, Optional[str]]:
    """验证日期格式（YYYY-MM-DD）"""
    if not date_str:
        return False, "日期不能为空"
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True, None
    except ValueError:
        return False, f"日期格式不正确：'{date_str}'，应为 YYYY-MM-DD 格式（例如：2025-01-13）"


def validate_repo_path(path: str) -> Tuple[bool, Optional[str]]:
    """验证 Git 仓库路径"""
    if not path:
        return False, "路径不能为空"
    repo_path = Path(path)
    if not repo_path.exists():
        return False, f"路径不存在：'{path}'"
    if not (repo_path / ".git").exists():
        return False, f"不是 Git 仓库：'{path}'（未找到 .git 目录）"
    return True, None


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


def get_week_day_name(date: datetime) -> str:
    """
    获取星期几的中文名称

    Args:
        date: 日期对象

    Returns:
        星期几的中文名称：周一、周二、...、周五、周六、周日
    """
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return weekdays[date.weekday()]


def is_weekday(date: datetime) -> bool:
    """
    判断是否是工作日（周一到周五）

    Args:
        date: 日期对象

    Returns:
        True表示工作日，False表示周末
    """
    return date.weekday() < 5  # 0-4是周一到周五，5-6是周六周日


def get_git_logs(
    repo_path: str,
    start_date: str,
    end_date: str
) -> List[Dict]:
    """
    获取单个Git仓库的日志

    Args:
        repo_path: Git仓库路径
        start_date: 开始日期（YYYY-MM-DD格式）
        end_date: 结束日期（YYYY-MM-DD格式）

    Returns:
        提交记录列表
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
            commit_date = commit.committed_datetime

            # 只保留工作日的提交（周一到周五）
            if not is_weekday(commit_date):
                continue

            commit_info = {
                "hash": commit.hexsha[:7],
                "author": commit.author.name,
                "email": commit.author.email,
                "message": commit.message.strip(),
                "date": commit_date.strftime("%Y-%m-%d"),
                "time": commit_date.strftime("%H:%M"),
                "weekday": get_week_day_name(commit_date)
            }

            commits_data.append(commit_info)

    except Exception as e:
        print(f"错误：获取Git日志失败 {repo_path}: {e}")
        return []

    return commits_data


def group_by_weekday(commits: List[Dict]) -> Dict[str, List[Dict]]:
    """
    按星期几分组提交记录

    Args:
        commits: 提交记录列表

    Returns:
        按星期几分组的字典
    """
    grouped = {
        "周一": [],
        "周二": [],
        "周三": [],
        "周四": [],
        "周五": []
    }

    for commit in commits:
        weekday = commit["weekday"]
        if weekday in grouped:
            grouped[weekday].append(commit)

    return grouped


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="获取Git日志并按周一到周五分组"
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

    args = parser.parse_args()

    # ===== 新增：输入验证 =====
    errors = []

    # 验证日期
    is_valid, error = validate_date(args.since)
    if not is_valid:
        errors.append(f"开始日期：{error}")

    is_valid, error = validate_date(args.until)
    if not is_valid:
        errors.append(f"结束日期：{error}")

    # 验证路径
    paths = [p.strip() for p in args.paths.split(",")]
    for path in paths:
        is_valid, error = validate_repo_path(path)
        if not is_valid:
            errors.append(error)

    # 如果有错误，打印并退出
    if errors:
        print_validation_error(errors)
        sys.exit(1)
    # ===== 验证结束 =====

    # 解析项目路径（已在上面完成）
    # paths = [p.strip() for p in args.paths.split(",")]  # 删除这行

    # 获取所有项目的日志
    all_commits = []

    for path in paths:
        print(f"正在获取 {path} 的日志...")
        commits = get_git_logs(path, args.since, args.until)
        all_commits.extend(commits)

    # 按星期几分组
    grouped = group_by_weekday(all_commits)

    # 统计信息
    total_commits = sum(len(commits) for commits in grouped.values())

    # 如果没有提交记录，给用户友好提示
    if total_commits == 0:
        print(f"\n⚠️ 警告：在 {args.since} 至 {args.until} 期间没有找到工作日的提交记录")
        print("   请检查：")
        print("   1. 日期范围是否正确")
        print("   2. 项目是否有提交记录")
        print("   3. 提交是否都在周末")
        print()

    result = {
        "start_date": args.since,
        "end_date": args.until,
        "total_commits": total_commits,
        "commits_by_day": grouped
    }

    # 输出JSON（到文件或控制台）
    json_output = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        # 输出到文件，避免控制台编码问题
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_output)
        print(f"✅ 结果已保存到：{args.output}")
    else:
        # 输出到控制台
        print(json_output)


if __name__ == "__main__":
    main()
