#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
周报生成器公共工具模块

功能：
- Windows 控制台编码修复
- 通用变量提取函数
- 输入验证函数

作者：老王
日期：2026-01-20
"""

import sys
import io
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional


# ========== 常量定义 ==========

WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def fix_windows_console_encoding() -> None:
    """
    修复 Windows 控制台编码问题（支持 emoji 和中文）

    在 Windows 上运行时必须调用此函数，否则无法正确显示中文和 emoji
    """
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def extract_variables(
    content: str,
    required_vars: List[str] | None = None
) -> Dict[str, Dict[str, Any]]:
    """
    从文本中提取变量占位符（{{变量名}}）

    Args:
        content: 要分析的文本内容
        required_vars: 必需变量列表（用于标记哪些变量是必需的）

    Returns:
        {占位符: {name: 变量名, description: 描述, required: 是否必需}}
    """
    if required_vars is None:
        required_vars = ["起始日期", "结束日期", "工作内容列表", "工作内容", "问题和风险"]

    variables = {}
    variable_pattern = re.compile(r'\{\{(.+?)\}\}')

    for match in variable_pattern.finditer(content):
        placeholder = match.group(0)
        var_name = match.group(1).strip()
        is_required = any(req in var_name for req in required_vars)

        variables[placeholder] = {
            "name": var_name,
            "description": f"变量：{var_name}",
            "required": is_required
        }

    return variables


def validate_date(date_str: str) -> Tuple[bool, Optional[str]]:
    """
    验证日期格式（YYYY-MM-DD）

    Args:
        date_str: 日期字符串

    Returns:
        (是否有效, 错误信息)
    """
    if not date_str:
        return False, "日期不能为空"
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True, None
    except ValueError:
        return False, f"日期格式不正确：'{date_str}'，应为 YYYY-MM-DD 格式（例如：2025-01-13）"


def validate_repo_path(path: str) -> Tuple[bool, Optional[str]]:
    """
    验证 Git 仓库路径

    Args:
        path: 路径字符串

    Returns:
        (是否有效, 错误信息)
    """
    if not path:
        return False, "路径不能为空"
    repo_path = Path(path)
    if not repo_path.exists():
        return False, f"路径不存在：'{path}'"
    if not (repo_path / ".git").exists():
        return False, f"不是 Git 仓库：'{path}'（未找到 .git 目录）"
    return True, None


def get_week_day_name(date: datetime) -> str:
    """
    获取星期几的中文名称（周一到周日）

    Args:
        date: 日期对象

    Returns:
        星期几的中文名称：周一、周二、周三、周四、周五、周六、周日
    """
    return WEEKDAYS[date.weekday()]
