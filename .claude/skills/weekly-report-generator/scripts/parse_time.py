#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能时间解析脚本

功能：
- 解析相对时间表达（本周/上周/本月/上月/本年/去年）
- 解析绝对时间范围（YYYY-MM-DD-YYYY-MM-DD）
- 解析单个日期并计算所在周（YYYY-MM-DD）
- 按自然周（周一到周日）划分时间范围
- 生成标准化的周任务清单数据
- 支持Windows环境
- UTF-8编码输出

作者：老王
日期：2026-01-20
"""

import sys
import json
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# 导入公共模块
try:
    from .common import fix_windows_console_encoding, WEEKDAYS
except ImportError:
    # 直接运行时使用绝对导入
    from common import fix_windows_console_encoding, WEEKDAYS

# 修复 Windows 控制台编码问题
fix_windows_console_encoding()


# ========== 辅助函数 ==========

def normalize_date(date_str: str) -> Optional[str]:
    """
    标准化日期格式为 YYYY-MM-DD

    Args:
        date_str: 日期字符串（支持多种分隔符）

    Returns:
        标准化后的日期字符串或None
    """
    date_str = date_str.strip()

    # 尝试多种分隔符: - . /
    patterns = [
        r'^(\d{4})[-./](\d{1,2})[-./](\d{1,2})$',
    ]

    for pattern in patterns:
        match = re.match(pattern, date_str)
        if match:
            year, month, day = match.groups()
            try:
                dt = datetime(int(year), int(month), int(day))
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                return None

    return None


def get_week_start_end(date: datetime) -> tuple[datetime, datetime]:
    """
    获取日期所在周的周一和周日

    Args:
        date: 日期对象

    Returns:
        (周一, 周日) 的日期对象
    """
    weekday = date.weekday()  # 0=周一, 6=周日
    monday = date - timedelta(days=weekday)
    sunday = monday + timedelta(days=6)
    return monday, sunday


def get_workdays_range(date: datetime) -> tuple[datetime, datetime]:
    """
    获取日期所在周的工作日范围（周一到周五）

    Args:
        date: 日期对象

    Returns:
        (周一, 周五) 的日期对象
    """
    weekday = date.weekday()  # 0=周一, 6=周日
    monday = date - timedelta(days=weekday)
    friday = monday + timedelta(days=4)
    return monday, friday


def split_by_weeks(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    将时间范围按自然周（周一到周日）划分

    Args:
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）

    Returns:
        周数列表
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    # 找到start所在周的周一
    start_weekday = start.weekday()
    monday = start - timedelta(days=start_weekday)

    weeks = []
    current_start = monday
    week_num = 1

    while current_start <= end:
        current_end = current_start + timedelta(days=6)
        if current_end > end:
            current_end = end

        week_start = max(current_start, start)

        weeks.append({
            "week": week_num,
            "start": week_start.strftime("%Y-%m-%d"),
            "end": current_end.strftime("%Y-%m-%d")
        })

        current_start = current_end + timedelta(days=1)
        week_num += 1

    return weeks


def generate_description(start_date: str, end_date: str) -> str:
    """
    生成用户友好的时间范围描述

    Args:
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）

    Returns:
        友好描述字符串
    """
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    start_weekday = WEEKDAYS[start_dt.weekday()]
    end_weekday = WEEKDAYS[end_dt.weekday()]

    return f"{start_date}({start_weekday})至{end_date}({end_weekday})"


# ========== 时间解析函数 ==========

def parse_relative_time(expr: str) -> Optional[Dict[str, Any]]:
    """
    解析相对时间表达式

    Args:
        expr: 相对时间表达式（本周/上周/本月/上月/本年/去年）

    Returns:
        时间范围字典或None
    """
    expr = expr.strip()
    today = datetime.now()

    if expr == "本周":
        # 当前周的周一到周五
        start, end = get_workdays_range(today)

    elif expr == "上周":
        # 上周的周一到周五
        last_week = today - timedelta(days=7)
        start, end = get_workdays_range(last_week)

    elif expr == "本月":
        # 本月1日到最后一日
        start = datetime(today.year, today.month, 1)
        if today.month == 12:
            next_month = datetime(today.year + 1, 1, 1)
        else:
            next_month = datetime(today.year, today.month + 1, 1)
        end = next_month - timedelta(days=1)

    elif expr == "上月":
        # 上月1日到最后一日
        if today.month == 1:
            # 去年12月
            start = datetime(today.year - 1, 12, 1)
            end = datetime(today.year, 1, 1) - timedelta(days=1)
        else:
            start = datetime(today.year, today.month - 1, 1)
            end = datetime(today.year, today.month, 1) - timedelta(days=1)

    elif expr == "本年":
        # 本年1月1日到12月31日
        start = datetime(today.year, 1, 1)
        end = datetime(today.year, 12, 31)

    elif expr == "去年":
        # 去年1月1日到12月31日
        start = datetime(today.year - 1, 1, 1)
        end = datetime(today.year - 1, 12, 31)

    else:
        return None

    return {
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d")
    }


def parse_absolute_range(expr: str) -> Optional[Dict[str, Any]]:
    """
    解析绝对时间范围表达式

    Args:
        expr: 时间范围字符串（YYYY-M-D-YYYY-M-D）

    Returns:
        时间范围字典或None
    """
    # 匹配两种分隔符: - 或 .
    # 格式: YYYY-M-D-YYYY-M-D 或 YYYY.M.D-YYYY.M.D
    match = re.match(
        r'^(\d{4})[-./](\d{1,2})[-./](\d{1,2})[-~～](\d{4})[-./](\d{1,2})[-./](\d{1,2})$',
        expr.strip()
    )

    if not match:
        return None

    start_year, start_month, start_day, end_year, end_month, end_day = match.groups()

    start_date = normalize_date(f"{start_year}-{start_month}-{start_day}")
    end_date = normalize_date(f"{end_year}-{end_month}-{end_day}")

    if not start_date or not end_date:
        return None

    # 验证日期逻辑
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    if start_dt > end_dt:
        return None

    return {
        "start": start_date,
        "end": end_date
    }


def parse_single_date(expr: str) -> Optional[Dict[str, Any]]:
    """
    解析单个日期并计算所在周

    Args:
        expr: 单个日期字符串

    Returns:
        该日期所在周（周一到周日）的时间范围字典
    """
    date_normalized = normalize_date(expr.strip())
    if not date_normalized:
        return None

    date_dt = datetime.strptime(date_normalized, "%Y-%m-%d")
    monday, sunday = get_week_start_end(date_dt)

    return {
        "start": monday.strftime("%Y-%m-%d"),
        "end": sunday.strftime("%Y-%m-%d")
    }


# ========== 主解析函数 ==========

def _build_success_result(expression: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    构建成功解析结果字典

    Args:
        expression: 原始时间表达式
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）

    Returns:
        成功结果字典
    """
    weeks = split_by_weeks(start_date, end_date)
    return {
        "success": True,
        "expression": expression,
        "start_date": start_date,
        "end_date": end_date,
        "start_weekday": WEEKDAYS[datetime.strptime(start_date, "%Y-%m-%d").weekday()],
        "end_weekday": WEEKDAYS[datetime.strptime(end_date, "%Y-%m-%d").weekday()],
        "weeks": weeks,
        "total_weeks": len(weeks),
        "description": generate_description(start_date, end_date)
    }


def parse_time_expression(time_expr: str) -> Dict[str, Any]:
    """
    解析时间表达式的主函数

    Args:
        time_expr: 时间表达式

    Returns:
        解析结果字典
    """
    # 按优先级尝试各种解析方式
    parsers = [
        parse_relative_time,
        parse_absolute_range,
        parse_single_date
    ]

    for parser in parsers:
        result = parser(time_expr)
        if result:
            return _build_success_result(time_expr, result["start"], result["end"])

    # 所有解析方式都失败
    return {
        "success": False,
        "error": f"无法解析时间表达式: '{time_expr}'",
        "suggestion": "支持的格式: 本周/上周/本月/上月/本年/去年, YYYY-MM-DD, YYYY-MM-DD-YYYY-MM-DD"
    }


# ========== 主函数 ==========

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="智能时间解析脚本 - 解析时间表达式并生成周任务清单",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 解析相对时间
  python parse_time.py --expression "本周"
  python parse_time.py --expression "本月"

  # 解析绝对时间范围
  python parse_time.py --expression "2025-5-1-2025-6-1"

  # 解析单个日期
  python parse_time.py --expression "2025-6-15"

  # 输出到JSON文件
  python parse_time.py --expression "本周" --output "./time_result.json"
        """
    )

    parser.add_argument(
        "--expression",
        type=str,
        required=True,
        help="时间表达式"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="输出JSON文件路径（可选，不提供则打印到控制台）"
    )

    args = parser.parse_args()

    # 解析时间表达式
    print(f"⏳ 正在解析时间表达式: {args.expression}")
    result = parse_time_expression(args.expression)

    # 输出结果
    json_str = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        # 输出到文件
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_str)
        print(f"✅ 解析结果已保存到: {output_path}")
    else:
        # 打印到控制台
        print()
        print("-" * 60)
        print(json_str)
        print("-" * 60)

    # 如果解析失败，退出码为1
    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
