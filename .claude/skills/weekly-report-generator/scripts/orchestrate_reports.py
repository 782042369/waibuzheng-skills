#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
周报生成编排脚本

功能：
- 一键完成周报生成的所有准备工作
- 自动解析时间、验证路径、分析模板
- 为每个周生成独立的任务配置文件
- 生成主调用提示（供 Claude Code 执行）

作者：老王
日期：2026-01-21
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess

# 导入公共模块
try:
    from .common import fix_windows_console_encoding, validate_repo_path
except ImportError:
    from common import fix_windows_console_encoding, validate_repo_path

# 修复 Windows 控制台编码问题
fix_windows_console_encoding()


# ========== 辅助函数 ==========

def run_parse_time(expression: str, output_path: str) -> Dict[str, Any]:
    """
    调用 parse_time.py 解析时间

    Args:
        expression: 时间表达式
        output_path: 输出JSON文件路径

    Returns:
        解析结果字典
    """
    script_path = Path(__file__).parent / "parse_time.py"
    cmd = [
        sys.executable,
        str(script_path),
        "--expression", expression,
        "--output", output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

    if result.returncode != 0:
        print(f"❌ 时间解析失败：{result.stderr}")
        sys.exit(1)

    # 读取结果
    with open(output_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_analyze_template(template_path: str, output_path: str) -> Optional[Dict[str, Any]]:
    """
    调用 analyze_template.py 分析模板

    Args:
        template_path: 模板文件路径
        output_path: 输出JSON文件路径

    Returns:
        模板结构字典（如果模板存在）
    """
    script_path = Path(__file__).parent / "analyze_template.py"
    cmd = [
        sys.executable,
        str(script_path),
        "--template", template_path,
        "--output", output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

    if result.returncode != 0:
        print(f"❌ 模板分析失败：{result.stderr}")
        sys.exit(1)

    # 读取结果
    with open(output_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_project_paths(paths: List[str]) -> None:
    """
    验证所有项目路径

    Args:
        paths: 项目路径列表

    Raises:
        SystemExit: 如果路径无效
    """
    errors = []

    for path in paths:
        is_valid, error = validate_repo_path(path)
        if not is_valid:
            errors.append(error)

    if errors:
        print("\n❌ 项目路径验证失败！")
        print("请检查以下问题：\n")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
        print()
        sys.exit(1)


def validate_output_path(output_path: str) -> Path:
    """
    验证输出路径并创建tmp子目录

    Args:
        output_path: 输出路径

    Returns:
        tmp目录的Path对象
    """
    output = Path(output_path)

    # 创建输出目录
    output.mkdir(parents=True, exist_ok=True)

    # 创建tmp子目录
    tmp_dir = output / "tmp"
    tmp_dir.mkdir(exist_ok=True)

    return tmp_dir


def extract_required_sections(template_structure: Dict[str, Any]) -> List[str]:
    """
    从模板结构中提取需要补充的章节

    Args:
        template_structure: 模板结构字典

    Returns:
        需要补充的章节列表
    """
    required_sections = []
    variables = template_structure.get("variables", {})

    # 检查各个变量是否存在
    if "future_plan" in variables or "下周计划" in variables:
        required_sections.append("future_plan")
    if "summary" in variables or "本周总结" in variables:
        required_sections.append("summary")
    if "risk" in variables or "问题和风险" in variables:
        required_sections.append("risk")

    return required_sections


def generate_week_tasks(
    weeks: List[Dict[str, Any]],
    project_paths: List[str],
    output_path: Path,
    template_path: Optional[str],
    output_format: str,
    template_structure: Optional[Dict[str, Any]],
    required_sections: List[str]
) -> List[Dict[str, Any]]:
    """
    为每个周生成任务配置文件

    Args:
        weeks: 周列表
        project_paths: 项目路径列表
        output_path: 输出路径
        template_path: 模板路径（可选）
        output_format: 输出格式
        template_structure: 模板结构（可选）
        required_sections: 需要补充的章节

    Returns:
        任务列表
    """
    tasks = []

    for week_info in weeks:
        week_num = week_info["week"]
        start_date = week_info["start"]
        end_date = week_info["end"]

        # 生成任务配置
        task_config = {
            "week": week_num,
            "start_date": start_date,
            "end_date": end_date,
            "project_paths": project_paths,
            "output_path": str(output_path),
            "template_path": template_path,
            "output_format": output_format,
            "required_sections": required_sections,
            "tmp_files": {
                "log": f"tmp/week_{week_num}-log.json",
                "report": f"tmp/week_{week_num}-report.json"
            }
        }

        # 保存任务配置
        task_file = output_path / "tmp" / f"week_{week_num}-task.json"
        with open(task_file, "w", encoding="utf-8") as f:
            json.dump(task_config, f, ensure_ascii=False, indent=2)

        tasks.append(task_config)

    return tasks


def print_confirmation(
    time_result: Dict[str, Any],
    project_paths: List[str],
    template_path: Optional[str],
    output_path: str,
    output_format: str,
    required_sections: List[str]
) -> None:
    """
    打印二次确认信息

    Args:
        time_result: 时间解析结果
        project_paths: 项目路径列表
        template_path: 模板路径
        output_path: 输出路径
        output_format: 输出格式
        required_sections: 需要补充的章节
    """
    print("\n⏳ 准备工作完成！请确认以下信息：\n")

    # 时间范围
    description = time_result.get("description", "")
    print(f"📅 时间范围: {description}")

    # 生成周报数
    total_weeks = time_result.get("total_weeks", 0)
    print(f"📊 生成周报: {total_weeks}份")

    # 项目路径
    print(f"📁 项目路径: ({len(project_paths)}个)")
    for i, path in enumerate(project_paths, 1):
        print(f"   {i}. {path}")

    # 模板文件
    if template_path:
        print(f"📄 模板文件: {template_path}")

    # 输出路径
    print(f"💾 输出路径: {output_path}")

    # 输出格式
    format_name = "Markdown (.md)" if output_format == ".md" else "Word (.docx)"
    print(f"📝 输出格式: {format_name}")

    # 需要补充的章节
    if required_sections:
        section_names = {
            "future_plan": "下周工作计划",
            "summary": "本周总结",
            "risk": "问题和风险"
        }
        section_list = [section_names[s] for s in required_sections]
        print(f"✨ 补充章节: {', '.join(section_list)}")

    print()


def generate_claude_call_instruction(
    output_path: Path,
    tasks: List[Dict[str, Any]]
) -> None:
    """
    生成 Claude Code 调用说明

    Args:
        output_path: 输出路径
        tasks: 任务列表
    """
    instruction_file = output_path / "tmp" / "claude_instruction.md"

    content = """# 周报生成任务

所有准备工作已完成！现在请 Claude Code 执行以下步骤：

## Step 1: 并行处理每个周报

使用 Task 工具并行启动多个 general-purpose 子智能体，每个子智能体处理一个周报。

**子智能体的任务提示**（复制以下内容，替换 `{week_num}` 等占位符）：

```
你是一个周报生成助手。请独立完成第 {week_num} 周周报的生成任务。

**任务配置文件**:
读取文件：{output_path}/tmp/week_{week_num}-task.json

**你的任务**:
1. 读取任务配置，获取参数
2. 调用 scripts/get_git_logs.py 获取Git日志
   参数：--paths "{project1},{project2}" --since {start_date} --until {end_date} --output "{output_path}/tmp/week_{week_num}-log.json"

3. 读取Git日志文件：{output_path}/tmp/week_{week_num}-log.json

4. **AI清洗技术术语**（必须）
   - 读取 references/report-prompts.md 了解清洗规则
   - 将技术术语转换为业务语言
   - 智能合并相似的提交记录
   - 按业务价值分级
   - 输出清洗后的工作内容

5. 保存清洗后的内容到：{output_path}/tmp/week_{week_num}-report.json
   JSON格式示例：
   ```json
   {{
     "title": "第{week_num}周周报（{start_date} 至 {end_date}）",
     "sections": [
       {{"title": "本周工作情况：", "content": "清洗后的工作内容"}},
       {{"title": "下周工作计划：", "content": "AI补充的计划"}},
       {{"title": "需协调解决问题：", "content": "AI补充的问题"}}
     ]
   }}
   ```

6. **AI补充主智能体指定的章节**（必须）
   - 基于本周工作内容推测下周计划
   - 基于本周工作内容推断问题和风险
   - 更新 week_{week_num}-report.json

7. 调用 scripts/fill_template.py 填充模板并导出
   参数：--template "{template_path}" --data "{output_path}/tmp/week_{week_num}-report.json" --output "{output_path}/第{week_num}周周报.{ext}"

8. 返回成功/失败状态
```

## Step 2: 汇总结果

所有子任务完成后，汇总结果并清理临时文件。

**清理规则**：
- 成功的任务：删除 tmp/week_XX-log.json 和 tmp/week_XX-report.json
- 失败的任务：保留用于调试
- 最终：只保留正式周报文件
"""

    with open(instruction_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"📝 调用说明已生成：{instruction_file}")
    print()


# ========== 主函数 ==========

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="周报生成编排脚本 - 一键完成所有准备工作",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成本月的周报（Markdown格式）
  python orchestrate_reports.py --paths "E:\\项目1,E:\\项目2" --time "本月" --output "E:\\周报"

  # 使用Word模板
  python orchestrate_reports.py --paths "E:\\项目1" --time "本周" --output "E:\\周报" --template "E:\\模板.docx" --format docx

  # 指定时间范围
  python orchestrate_reports.py --paths "E:\\项目1" --time "2025-1-1-2025-1-31" --output "E:\\周报"
        """
    )

    parser.add_argument(
        "--paths",
        type=str,
        required=True,
        help="项目路径列表，用逗号分隔（如：path1,path2）"
    )
    parser.add_argument(
        "--time",
        type=str,
        required=True,
        help="时间表达式（本周/上周/本月/上月/本年/去年/YYYY-MM-DD/YYYY-MM-DD-YYYY-MM-DD）"
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="输出目录路径"
    )
    parser.add_argument(
        "--template",
        type=str,
        help="模板文件路径（可选，支持.md和.docx）"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["md", "docx"],
        default="md",
        help="输出格式（默认: md）"
    )
    parser.add_argument(
        "--no-confirm",
        action="store_true",
        help="跳过二次确认，直接执行"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("🚀 周报生成编排脚本启动")
    print("=" * 60)
    print()

    # 解析项目路径
    project_paths = [p.strip() for p in args.paths.split(",")]

    # 验证项目路径
    print("🔍 验证项目路径...")
    validate_project_paths(project_paths)
    print(f"✅ 所有项目路径有效")

    # 验证输出路径
    print("🔍 验证输出路径...")
    tmp_dir = validate_output_path(args.output)
    print(f"✅ 输出路径有效: {args.output}")
    print(f"✅ 临时目录已创建: {tmp_dir}")

    # 解析时间
    print("⏳ 解析时间表达式...")
    time_result_path = tmp_dir / "time_result.json"
    time_result = run_parse_time(args.time, str(time_result_path))
    print(f"✅ 时间解析成功: {time_result['description']}")

    # 分析模板（如果提供）
    template_structure = None
    required_sections = []

    if args.template:
        print("🔍 分析模板文件...")
        template_structure_path = tmp_dir / "template_structure.json"
        template_structure = run_analyze_template(args.template, str(template_structure_path))
        print(f"✅ 模板分析成功")

        # 提取需要补充的章节
        required_sections = extract_required_sections(template_structure)
        if required_sections:
            print(f"✅ 检测到需要补充的章节: {required_sections}")
    else:
        print("⏭️  未提供模板，跳过分析")

    # 生成周任务配置
    print("📋 生成周任务配置...")
    weeks = time_result["weeks"]
    output_format_ext = f".{args.format}"

    tasks = generate_week_tasks(
        weeks=weeks,
        project_paths=project_paths,
        output_path=Path(args.output),
        template_path=args.template,
        output_format=output_format_ext,
        template_structure=template_structure,
        required_sections=required_sections
    )

    print(f"✅ 已生成 {len(tasks)} 个周任务配置")
    print()

    # 二次确认
    if not args.no_confirm:
        print_confirmation(
            time_result=time_result,
            project_paths=project_paths,
            template_path=args.template,
            output_path=args.output,
            output_format=output_format_ext,
            required_sections=required_sections
        )

        response = input("确认吗？(输入'确认'开始生成，其他任意键取消): ")
        if response != "确认":
            print("❌ 已取消")
            sys.exit(0)

    # 生成 Claude Code 调用说明
    print("📝 生成 Claude Code 调用说明...")
    generate_claude_call_instruction(Path(args.output), tasks)

    print("=" * 60)
    print("✅ 准备工作完成！")
    print("=" * 60)
    print()
    print("📋 下一步操作：")
    print("   1. 阅读 Claude Code 调用说明：{}/tmp/claude_instruction.md".format(args.output))
    print("   2. 在 Claude Code 中执行调用说明中的步骤")
    print()


if __name__ == "__main__":
    main()
