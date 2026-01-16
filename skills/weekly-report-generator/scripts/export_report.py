#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
周报导出脚本（重构版）

功能：
- 将AI生成的完整周报内容写入文件
- 支持Markdown、Word两种格式
- 根据文件名扩展名自动检测输出格式
- 支持自动文件名生成
- 支持日期格式化（用于文件名）
- 使用专业的 Markdown → Word 转换器

作者：老王
日期：2026-01-16
"""

import sys
import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import Optional


# ========== Markdown → Word 转换器（改进版） ==========

class MarkdownToWordConverter:
    """
    Markdown 到 Word 的专业转换器

    相比正则表达式，更稳定地处理 Markdown 语法
    """

    def __init__(self):
        self.lines = []
        self.current_idx = 0

    def convert(self, markdown_content: str, doc) -> None:
        """
        将 Markdown 内容转换并添加到 Word 文档

        Args:
            markdown_content: Markdown 文本
            doc: docx.Document 对象
        """
        self.lines = markdown_content.split('\n')
        self.current_idx = 0

        while self.current_idx < len(self.lines):
            line = self.lines[self.current_idx].rstrip()

            # 空行
            if not line:
                doc.add_paragraph()
                self.current_idx += 1
                continue

            # 标题（# 开头）
            if line.startswith('#'):
                self._add_heading(doc, line)
                self.current_idx += 1
                continue

            # 分隔线（--- 或 ***）
            if line.strip() in ('---', '***', '___'):
                doc.add_paragraph('_' * 50)
                self.current_idx += 1
                continue

            # 代码块（``` 开头）
            if line.strip().startswith('```'):
                self._add_code_block(doc)
                continue

            # 引用（> 开头）
            if line.startswith('>'):
                self._add_blockquote(doc, line)
                self.current_idx += 1
                continue

            # 列表（- 或 * 或 数字. 开头）
            if re.match(r'^(\s*)([-*]|\d+\.)\s+', line):
                self._add_list_item(doc, line)
                self.current_idx += 1
                continue

            # 普通段落（可能跨行）
            self._add_paragraph(doc)

    def _add_heading(self, doc, line: str) -> None:
        """添加标题"""
        level = min(len(line) - len(line.lstrip('#')), 6)
        text = line.lstrip('#').strip()

        heading = doc.add_heading(text, level=level)

        # 处理标题中的行内格式
        self._apply_inline_formatting(heading, text)

    def _add_paragraph(self, doc) -> None:
        """添加段落（可能跨行）"""
        paragraph_lines = []

        while self.current_idx < len(self.lines):
            line = self.lines[self.current_idx].rstrip()

            # 遇到特殊语法，结束段落
            if (not line or
                line.startswith('#') or
                line.strip() in ('---', '***', '___') or
                re.match(r'^(\s*)([-*]|\d+\.)\s+', line) or
                line.strip().startswith('```') or
                line.startswith('>')):
                break

            paragraph_lines.append(line)
            self.current_idx += 1

        if paragraph_lines:
            para_text = "\n".join(paragraph_lines)
            para = doc.add_paragraph()
            self._apply_inline_formatting(para, para_text)

    def _add_list_item(self, doc, line: str) -> None:
        """添加列表项"""
        # 判断列表类型
        if re.match(r'^\s*\d+[\.\)]\s+', line):
            style = 'List Number'
        else:
            style = 'List Bullet'

        # 移除列表标记
        text = re.sub(r'^(\s*)([-*]|\d+[\.\)])\s+', '', line)

        para = doc.add_paragraph(style=style)
        self._apply_inline_formatting(para, text)

    def _add_code_block(self, doc) -> None:
        """添加代码块"""
        # 跳过开始的 ```
        self.current_idx += 1

        code_lines = []
        while self.current_idx < len(self.lines):
            line = self.lines[self.current_idx]
            if line.strip().startswith('```'):
                self.current_idx += 1
                break
            code_lines.append(line)
            self.current_idx += 1

        code_text = "\n".join(code_lines)
        para = doc.add_paragraph(code_text)
        para.style = 'No Spacing'
        try:
            from docx.shared import Pt
            for run in para.runs:
                run.font.name = 'Courier New'
                run.font.size = Pt(9)
        except ImportError:
            pass

    def _add_blockquote(self, doc, line: str) -> None:
        """添加引用"""
        text = line.lstrip('>').strip()
        para = doc.add_paragraph(text)
        # 引用样式：斜体
        for run in para.runs:
            run.italic = True

    def _apply_inline_formatting(self, element, text: str) -> None:
        """应用行内格式（粗体、斜体、代码）"""
        # 清空元素
        if hasattr(element, 'clear'):
            element.clear()

        # 解析行内格式
        parts = re.split(r'(\*\*.*?\*\*|__.*?__|_.*?_|\*.*?\*|`.*?`)', text)

        for part in parts:
            if not part:
                continue

            # 粗体
            if (part.startswith('**') and part.endswith('**')) or \
               (part.startswith('__') and part.endswith('__')):
                content = part[2:-2]
                run = element.add_run(content)
                run.bold = True

            # 斜体
            elif (part.startswith('_') and part.endswith('_') and not
                  part.startswith('__')):
                content = part[1:-1]
                run = element.add_run(content)
                run.italic = True

            # 代码
            elif part.startswith('`') and part.endswith('`'):
                content = part[1:-1]
                run = element.add_run(content)
                run.font.name = 'Courier New'

            # 普通文本
            else:
                element.add_run(part)


# ========== 原有的辅助函数 ==========

def format_date_for_filename(start_date: str, end_date: str) -> str:
    """
    格式化日期范围用于文件名

    Args:
        start_date: 开始日期（YYYY-MM-DD格式）
        end_date: 结束日期（YYYY-MM-DD格式）

    Returns:
        格式化的日期字符串，如："20250113-20250117"
    """
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    start_formatted = start_dt.strftime("%Y%m%d")
    end_formatted = end_dt.strftime("%Y%m%d")

    return f"{start_formatted}-{end_formatted}"


def generate_auto_filename(start_date: str, end_date: str) -> str:
    """
    自动生成文件名（默认 Markdown 格式）

    Args:
        start_date: 开始日期（YYYY-MM-DD格式）
        end_date: 结束日期（YYYY-MM-DD格式）

    Returns:
        文件名，如："周报20250113-20250117.md"
    """
    date_str = format_date_for_filename(start_date, end_date)
    return f"周报{date_str}.md"


def detect_output_format(filename: str) -> str:
    """
    根据文件名检测输出格式

    Args:
        filename: 文件名

    Returns:
        输出格式（markdown/word）
    """
    suffix = Path(filename).suffix.lower()

    if suffix == ".docx":
        return "word"
    else:
        return "markdown"


def write_markdown_file(content: str, output_path: str, filename: str) -> str:
    """
    写入Markdown文件

    Args:
        content: 完整的周报内容（AI已生成）
        output_path: 输出目录路径
        filename: 文件名

    Returns:
        生成的文件完整路径
    """
    # 确保输出目录存在
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 保存文件
    output_file = output_dir / filename
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

    return str(output_file.resolve())


def write_word_file(content: str, output_path: str, filename: str) -> str:
    """
    写入Word文件，使用新的 Markdown → Word 转换器

    Args:
        content: 完整的周报内容（Markdown格式）
        output_path: 输出目录路径
        filename: 文件名

    Returns:
        生成的文件完整路径
    """
    try:
        from docx import Document
    except ImportError:
        raise ImportError(
            "需要安装 python-docx 库：pip install python-docx\n"
            "或使用 pandoc 转换：pandoc input.md -o output.docx"
        )

    # 确保输出目录存在
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 创建 Word 文档
    doc = Document()

    # 使用新的专业转换器
    converter = MarkdownToWordConverter()
    converter.convert(content, doc)

    # 保存文件
    output_file = output_dir / filename
    doc.save(output_file)

    return str(output_file.resolve())




def export_report(
    content: str,
    output_path: str,
    filename: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> str:
    """
    导出周报文件，根据 filename 扩展名自动检测输出格式

    Args:
        content: 完整的周报内容（AI已生成，Markdown格式）
        output_path: 输出目录路径
        filename: 文件名（可选，不提供则自动生成，默认 .md）
        start_date: 开始日期（可选，用于自动文件名）
        end_date: 结束日期（可选，用于自动文件名）

    Returns:
        生成的文件完整路径
    """
    # 如果未提供文件名，自动生成（默认 Markdown 格式）
    if not filename:
        if not start_date or not end_date:
            raise ValueError("未提供文件名时，必须提供 start_date 和 end_date 用于自动生成文件名")
        filename = generate_auto_filename(start_date, end_date)

    # 根据文件名扩展名自动检测输出格式
    output_format = detect_output_format(filename)

    # 根据格式调用对应的写入函数
    if output_format == "markdown":
        return write_markdown_file(content, output_path, filename)
    elif output_format == "word":
        return write_word_file(content, output_path, filename)
    else:
        raise ValueError(f"不支持的文件格式：{Path(filename).suffix}，请使用 .md 或 .docx")


def main():
    """主函数"""
    print("=" * 60)
    print("📝 周报导出脚本启动")
    print("=" * 60)
    print()

    parser = argparse.ArgumentParser(
        description="将AI生成的周报内容写入文件，支持Markdown/Word格式"
    )
    parser.add_argument(
        "--content",
        type=str,
        required=True,
        help="完整的周报内容（AI已生成，Markdown格式）"
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
        help="输出文件名（可选，不提供则自动生成）"
    )
    parser.add_argument(
        "--start-date",
        type=str,
        help="开始日期（YYYY-MM-DD格式，用于自动文件名）"
    )
    parser.add_argument(
        "--end-date",
        type=str,
        help="结束日期（YYYY-MM-DD格式，用于自动文件名）"
    )

    args = parser.parse_args()

    print("📋 输入参数：")
    print(f"  - 输出目录：{args.output}")
    print(f"  - 文件名：{args.filename if args.filename else '（自动生成）'}")
    if args.start_date and args.end_date:
        print(f"  - 日期范围：{args.start_date} 至 {args.end_date}")
    content_preview = args.content[:100] + "..." if len(args.content) > 100 else args.content
    print(f"  - 内容预览：{content_preview}")
    print()

    # 导出周报
    print("📤 正在导出周报...")
    try:
        # 检测文件名和格式
        if args.filename:
            filename = args.filename
            output_format = detect_output_format(filename)
            format_name = "Word (.docx)" if output_format == "word" else "Markdown (.md)"
            print(f"  - 文件名：{filename}")
            print(f"  - 输出格式：{format_name}")
        else:
            if not args.start_date or not args.end_date:
                raise ValueError("未提供文件名时，必须提供 start_date 和 end_date 用于自动生成文件名")
            filename = generate_auto_filename(args.start_date, args.end_date)
            print(f"  - 自动生成文件名：{filename}")
            print(f"  - 输出格式：Markdown (.md)")

        print()

        output_file = export_report(
            content=args.content,
            output_path=args.output,
            filename=args.filename,
            start_date=args.start_date,
            end_date=args.end_date
        )

        # 获取文件大小
        file_size = Path(output_file).stat().st_size
        size_kb = file_size / 1024

        print()
        print("✅ 周报导出成功")
        print(f"   文件路径：{output_file}")
        print(f"   文件大小：{file_size} 字节（{size_kb:.2f} KB）")

    except Exception as e:
        print()
        print(f"❌ 导出失败：{e}")
        print()
        print("💡 可能的原因：")
        print("   1. 输出目录不存在或无写入权限")
        print("   2. Word 格式需要安装 python-docx：pip install python-docx")
        print("   3. 内容格式不正确")
        import traceback
        print()
        print("详细错误信息：")
        traceback.print_exc()
        sys.exit(1)

    print()
    print("=" * 60)
    print("✅ 周报导出完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
