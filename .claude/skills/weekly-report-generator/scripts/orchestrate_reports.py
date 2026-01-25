#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""周报生成编排脚本

作者：老王
日期：2026-01-21
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess

try:
    from .common import fix_windows_console_encoding, validate_repo_path, extract_sections_from_structure
except ImportError:
    from common import fix_windows_console_encoding, validate_repo_path, extract_sections_from_structure

fix_windows_console_encoding()


def _run_script(script_name: str, args: List[str], output_path: str) -> Dict[str, Any]:
    """运行子脚本并返回JSON结果

    Args:
        script_name: 脚本文件名（如 "parse_time.py"）
        args: 命令行参数列表（不包括脚本名和output参数）
        output_path: 输出文件路径

    Returns:
        脚本输出的JSON数据

    Raises:
        SystemExit: 脚本执行失败时退出
    """
    script_path = Path(__file__).parent / script_name
    cmd = ["python3", str(script_path)] + args + ["--output", output_path]

    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

    if result.returncode != 0:
        print(f"❌ {script_name} 执行失败：{result.stderr}")
        sys.exit(1)

    output_file = Path(output_path)
    if not output_file.exists():
        print(f"❌ {script_name} 输出文件未生成：{output_path}")
        sys.exit(1)

    with open(output_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_parse_time(expression: str, output_path: str) -> Dict[str, Any]:
    """调用 parse_time.py 解析时间"""
    return _run_script("parse_time.py", ["--expression", expression], output_path)


def run_analyze_template(template_path: str, output_path: str) -> Dict[str, Any]:
    """调用 analyze_template.py 分析模板"""
    return _run_script("analyze_template.py", ["--template", template_path], output_path)


def validate_project_paths(paths: List[str]) -> None:
    """验证所有项目路径"""
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
    """验证输出路径并创建tmp子目录"""
    output = Path(output_path)
    output.mkdir(parents=True, exist_ok=True)

    tmp_dir = output / "tmp"
    tmp_dir.mkdir(exist_ok=True)

    return tmp_dir


def extract_template_sections(template_structure: Dict[str, Any]) -> List[str]:
    """从模板结构中提取章节标题列表

    Returns:
        章节标题列表，如：["本周工作情况：", "下周工作计划：", "需协调解决问题："]
    """
    return [
        section["title"]
        for section in extract_sections_from_structure(template_structure.get("structure", {}))
    ]


def generate_week_tasks(
    weeks: List[Dict[str, Any]],
    project_paths: List[str],
    output_path: Path,
    template_path: Optional[str],
    output_format: str,
    template_sections: Optional[List[str]],
    naming_rules: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """为每个周生成任务配置文件"""
    tasks = []

    for week_info in weeks:
        week_num = week_info["week"]
        start_date = week_info["start"]
        end_date = week_info["end"]

        # 获取命名规则（如果提供）
        output_filename = None
        if naming_rules and week_num <= len(naming_rules):
            output_filename = f"{naming_rules[week_num - 1]}{output_format}"

        task_config = {
            "week": week_num,
            "start_date": start_date,
            "end_date": end_date,
            "project_paths": project_paths,
            "output_path": str(output_path),
            "template_path": template_path,
            "output_format": output_format,
            "template_sections": template_sections,
            "output_filename": output_filename,
            "tmp_files": {
                "log": f"tmp/week_{week_num}-log.json",
                "report": f"tmp/week_{week_num}-report.json"
            }
        }

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
    template_sections: Optional[List[str]]
) -> None:
    """打印二次确认信息"""
    print("\n⏳ 准备工作完成！请确认以下信息：\n")
    print(f"📅 时间范围: {time_result.get('description', '')}")
    print(f"📊 生成周报: {time_result.get('total_weeks', 0)}份")
    print(f"📁 项目路径: ({len(project_paths)}个)")

    for i, path in enumerate(project_paths, 1):
        print(f"   {i}. {path}")

    if template_path:
        print(f"📄 模板文件: {template_path}")

    print(f"💾 输出路径: {output_path}")

    format_name = "Markdown (.md)" if output_format == ".md" else "Word (.docx)"
    print(f"📝 输出格式: {format_name}")

    if template_sections:
        print(f"📋 模板章节: ({len(template_sections)}个)")
        for section in template_sections:
            print(f"   - {section}")

    print()


def generate_claude_call_instruction(
    output_path: Path,
    tasks: List[Dict[str, Any]],
    naming_rules: Optional[List[str]] = None
) -> None:
    """生成 Claude Code 调用说明"""
    instruction_file = output_path / "tmp" / "claude_instruction.md"

    # 从第一个任务中提取模板章节信息
    template_sections_info = ""
    if tasks and tasks[0].get("template_sections"):
        sections = tasks[0]["template_sections"]
        if sections:
            sections_list = "\n".join([f'   - "{s}"' for s in sections])
            template_sections_info = f"""

**模板中的章节标题**:
{sections_list}

AI 需要为每个章节生成对应的 `content` 内容。
"""

    # 生成命名规则说明
    naming_info = ""
    if naming_rules:
        naming_list = "\n".join([f'   - 第{i+1}周: {name}' for i, name in enumerate(naming_rules)])
        naming_info = f"""

**自定义命名规则**:
{naming_list}

⚠️ 子智能体必须使用上述自定义文件名，不要使用默认的"第X周周报"格式。
"""

    content = f"""# 周报生成任务

所有准备工作已完成！现在请 Claude Code 执行以下步骤：

## Step 1: 并行处理每个周报

使用 Task 工具并行启动 general-purpose 子智能体。

**子智能体任务提示**（替换占位符）：

```
你是周报生成助手。请独立完成第 {{week_num}} 周周报。

**任务配置文件**:
{{output_path}}/tmp/week_{{week_num}}-task.json

**执行步骤**:
1. 读取 task JSON 获取参数

2. 调用 scripts/get_git_logs.py 获取日志
   参数：--paths "{{project1}},{{project2}}" --since {{start_date}} --until {{end_date}} --output "{{output_path}}/tmp/week_{{week_num}}-log.json"

3. 按 {{output_path}}/tmp/week_{{week_num}}-log.json

4. 生成 sections 格式 JSON 并保存到 {{output_path}}/tmp/week_{{week_num}}-report.json

5. 调用 fill_template.py 导出

**JSON 格式**:
```json
{{
  "title": "第{{week_num}}周周报",
  "sections": [
    {{"title": "本周工作情况：", "content": "1. xxx\\n2. xxx"}},
    {{"title": "下周工作计划：", "content": "1. xxx\\n2. xxx"}},
    {{"title": "需协调解决问题：", "content": "识别的问题和风险"}}
  ]
}}
```
{template_sections_info}{naming_info}
**返回状态**: "✅ 第{{week_num}}周周报生成成功" 或 "❌ 失败原因"
⚠️ 只返回简短状态，不要输出详细报告！
```

**变量替换**:
- {{week_num}} = 周数（1, 2, 3...）
- {{output_path}} = 输出目录路径
- 其他变量见 task JSON

## Step 2: 核心规则摘要

```
**周报清洗核心规则**：

【语言规范】
- 禁止按项目分组，统一编号

【推导规则】
完整规则：references/report-prompts.md
```

## Step 3: 汇总结果

清理临时文件（成功任务的临时文件删除，失败的保留）。
"""

    with open(instruction_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"📝 调用说明已生成：{instruction_file}")
    print()


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

  # 自定义周报命名规则（推荐）
  python orchestrate_reports.py --paths "E:\\项目1,E:\\项目2" --time "2025-6-30-2025-7-11" --output "E:\\周报" --template "E:\\模板.docx" --format docx --naming "华电第一周周报,华电第二周周报"
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
        "--naming",
        type=str,
        help="周报命名规则列表，用逗号分隔（如：第一周周报,第二周周报）"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("🚀 周报生成编排脚本启动")
    print("=" * 60)
    print()

    project_paths = [p.strip() for p in args.paths.split(",")]

    print("🔍 验证项目路径...")
    validate_project_paths(project_paths)
    print(f"✅ 所有项目路径有效")

    print("🔍 验证输出路径...")
    tmp_dir = validate_output_path(args.output)
    print(f"✅ 输出路径有效: {args.output}")
    print(f"✅ 临时目录已创建: {tmp_dir}")

    print("⏳ 解析时间表达式...")
    time_result_path = tmp_dir / "time_result.json"
    time_result = run_parse_time(args.time, str(time_result_path))
    print(f"✅ 时间解析成功: {time_result['description']}")

    template_structure = None
    template_sections = None

    if args.template:
        print("🔍 分析模板文件...")
        template_structure_path = tmp_dir / "template_structure.json"
        template_structure = run_analyze_template(args.template, str(template_structure_path))
        print(f"✅ 模板分析成功")

        template_sections = extract_template_sections(template_structure)
        if template_sections:
            print(f"✅ 检测到 {len(template_sections)} 个章节")
    else:
        print("⏭️  未提供模板，跳过分析")

    print("📋 生成周任务配置...")
    weeks = time_result["weeks"]
    output_format_ext = f".{args.format}"

    # 处理命名规则
    naming_rules = None
    if args.naming:
        naming_rules = [name.strip() for name in args.naming.split(",")]
        if len(naming_rules) != len(weeks):
            print(f"⚠️ 警告：命名规则数量({len(naming_rules)})与周数({len(weeks)})不匹配")
            print(f"   将只为前 {len(naming_rules)} 周应用自定义命名")

    tasks = generate_week_tasks(
        weeks=weeks,
        project_paths=project_paths,
        output_path=Path(args.output),
        template_path=args.template,
        output_format=output_format_ext,
        template_sections=template_sections,
        naming_rules=naming_rules
    )

    print(f"✅ 已生成 {len(tasks)} 个周任务配置")
    print()

    # 显示配置信息供AI确认
    print_confirmation(
        time_result=time_result,
        project_paths=project_paths,
        template_path=args.template,
        output_path=args.output,
        output_format=output_format_ext,
        template_sections=template_sections
    )

    print("📝 生成 Claude Code 调用说明...")
    generate_claude_call_instruction(Path(args.output), tasks, naming_rules)

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
