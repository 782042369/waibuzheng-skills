#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
周报导出脚本

功能：
- 根据模板格式化周报内容
- 保存到用户指定的路径和文件名
- 支持Markdown格式
- 使用Jinja2模板引擎

作者：老王
日期：2026-01-15
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict


# 默认周报模板
DEFAULT_TEMPLATE = """# 项目周报

**汇报周期**: {{起始日期}} - {{结束日期}}

## 本期工作内容

{{工作内容列表}}

## 存在问题和风险

{{问题和风险}}

---
**共{{提交次数}}次提交**
"""


def render_template(template: str, context: Dict) -> str:
    """
    使用Jinja2渲染模板

    Args:
        template: 模板内容
        context: 变量字典

    Returns:
        渲染后的内容
    """
    try:
        from jinja2 import Template
    except ImportError:
        print("错误：需要安装jinja2库")
        print("请运行：pip install jinja2")
        sys.exit(1)

    template_obj = Template(template)
    return template_obj.render(**context)


def format_date_range(start_date: str, end_date: str) -> tuple:
    """
    格式化日期范围

    Args:
        start_date: 开始日期（YYYY-MM-DD格式）
        end_date: 结束日期（YYYY-MM-DD格式）

    Returns:
        (格式化的起始日期, 格式化的结束日期)
        格式：2025年1月13日（周一）
    """
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    start_formatted = start_dt.strftime("%Y年%m月%d日") + f"（{weekdays[start_dt.weekday()]}）"
    end_formatted = end_dt.strftime("%Y年%m月%d日") + f"（{weekdays[end_dt.weekday()]}）"

    return start_formatted, end_formatted


def export_report(
    content: str,
    template: str,
    output_path: str,
    filename: str,
    start_date: str = None,
    end_date: str = None,
    total_commits: int = 0
) -> str:
    """
    导出周报文件

    Args:
        content: 周报内容（AI清洗后的）
        template: 模板内容
        output_path: 输出目录路径
        filename: 文件名
        start_date: 开始日期（可选）
        end_date: 结束日期（可选）
        total_commits: 提交次数（可选）

    Returns:
        生成的文件完整路径
    """
    # 确保输出目录存在
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 准备模板变量
    context = {
        "工作内容列表": content,
        "提交次数": total_commits
    }

    # 如果提供了日期，格式化
    if start_date and end_date:
        start_formatted, end_formatted = format_date_range(start_date, end_date)
        context["起始日期"] = start_formatted
        context["结束日期"] = end_formatted

    # 渲染模板
    rendered = render_template(template, context)

    # 保存文件
    output_file = output_dir / filename
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rendered)

    return str(output_file.resolve())


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="根据模板导出周报文件"
    )
    parser.add_argument(
        "--content",
        type=str,
        required=True,
        help="周报内容（清洗后的工作内容列表）"
    )
    parser.add_argument(
        "--template",
        type=str,
        help="模板内容（可选，使用默认模板如果不提供）"
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="输出目录路径"
    )
    parser.add_argument(
        "--filename",
        type=str,
        required=True,
        help="输出文件名（如：20250115周报.md）"
    )
    parser.add_argument(
        "--start-date",
        type=str,
        help="开始日期（YYYY-MM-DD格式，可选）"
    )
    parser.add_argument(
        "--end-date",
        type=str,
        help="结束日期（YYYY-MM-DD格式，可选）"
    )
    parser.add_argument(
        "--total-commits",
        type=int,
        default=0,
        help="提交次数（可选，默认0）"
    )

    args = parser.parse_args()

    # 默认模板
    if not args.template:
        args.template = DEFAULT_TEMPLATE
    else:
        # 如果提供了模板路径，读取文件内容
        template_path = Path(args.template)
        if template_path.exists() and template_path.is_file():
            try:
                with open(template_path, "r", encoding="utf-8") as f:
                    args.template = f.read()
            except Exception as e:
                print(f"警告：无法读取模板文件 {template_path}，使用默认模板")
                print(f"错误信息：{e}")
                args.template = DEFAULT_TEMPLATE

    # 导出周报
    output_file = export_report(
        content=args.content,
        template=args.template,
        output_path=args.output,
        filename=args.filename,
        start_date=args.start_date,
        end_date=args.end_date,
        total_commits=args.total_commits
    )

    print(f"周报已生成：{output_file}")


if __name__ == "__main__":
    main()
