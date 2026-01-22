#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""周报生成器公共工具模块

作者：老王
日期：2026-01-20
"""

import sys
import io
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional


WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def fix_windows_console_encoding() -> None:
    """修复 Windows 控制台编码问题（支持 emoji 和中文）"""
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def extract_variables(
    content: str,
    required_vars: Optional[List[str]] = None
) -> Dict[str, Dict[str, Any]]:
    """从文本中提取变量占位符（{{变量名}}）"""
    if required_vars is None:
        required_vars = ["起始日期", "结束日期", "工作内容列表", "工作内容", "问题和风险"]

    variables = {}
    variable_pattern = re.compile(r'\{\{(.+?)\}\}')

    for match in variable_pattern.finditer(content):
        placeholder = match.group(0)
        var_name = match.group(1).strip()
        variables[placeholder] = {
            "name": var_name,
            "required": any(req in var_name for req in required_vars)
        }

    return variables


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


def get_week_day_name(date: datetime) -> str:
    """获取星期几的中文名称（周一到周日）"""
    return WEEKDAYS[date.weekday()]


def extract_sections_from_structure(structure: Dict[str, Any]) -> List[Dict[str, Any]]:
    """从模板结构中提取章节列表

    Args:
        structure: 模板结构（来自 analyze_template.py 的输出）

    Returns:
        章节列表，每个章节包含 title 和 level
    """
    sections_data = structure.get("sections", [])
    result = []

    for section in sections_data:
        title = section.get("title", "").strip()
        if not title:
            continue

        result.append({
            "title": title,
            "level": section.get("level", 2)
        })

    return result
