"""
内容分析模块 - 工程制造业文章创作器
分析已验证的搜索结果，提取关键信息（针对管理层优化）
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict

# 添加scripts目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from common import logger, load_json, save_json


def analyze_content_for_management(validated_results_path: Path, output_path: Path) -> bool:
    """
    分析已验证的搜索结果，针对管理层优化

    分析重点（针对管理层）：
    - 市场趋势：市场规模、增长率、驱动因素、竞争格局
    - 商业价值：ROI、成本效益、竞争优势、投资回报期
    - 技术创新：技术突破、应用场景、效率提升、成本降低
    - 政策环境：政策红利、监管要求、行业标准
    - 案例效果：客户案例、实施效果、数据支撑、经验总结

    Args:
        validated_results_path: 已验证的搜索结果文件路径
        output_path: 输出文件路径

    Returns:
        是否执行成功
    """
    # 加载已验证的搜索结果
    validated_data = load_json(validated_results_path)
    if not validated_data:
        logger.error("加载验证结果失败")
        return False

    articles = validated_data.get("articles", [])
    logger.info(f"加载了 {len(articles)} 篇已验证的文章")

    logger.info("=" * 80)
    logger.info("开始内容分析（聚焦管理层视角）")
    logger.info("=" * 80)

    # 提取关键信息
    analysis_report = {
        "task_id": validated_data.get("task_id", ""),
        "market_trends": {
            "market_size": [],
            "growth_rate": [],
            "driving_factors": [],
            "competitive_landscape": []
        },
        "business_value": {
            "roi_cases": [],
            "cost_benefits": [],
            "competitive_advantages": [],
            "payback_period": []
        },
        "technology_innovation": {
            "breakthroughs": [],
            "applications": [],
            "efficiency_gains": [],
            "cost_reductions": []
        },
        "policy_environment": {
            "policy_supports": [],
            "regulatory_requirements": [],
            "industry_standards": []
        },
        "case_studies": [],
        "key_insights": [],
        "data_sources": validated_data.get("data_sources_summary", {}),
        "analysis_completed_at": datetime.now().isoformat()
    }

    # 分析每篇文章（只使用verified=true的数据）
    for article in articles:
        url = article.get("url", "")
        title = article.get("title", "")
        credibility_score = article.get("credibility_score", 0)
        data_points = article.get("data_points", [])

        # 只分析高质量文章（评分 >= 5.0）
        if credibility_score < 5.0:
            continue

        logger.info(f"分析文章：{title}")

        # 提取数据点中的关键信息
        for dp in data_points:
            if not dp.get("verified", False):
                continue

            data = dp.get("data", "")
            context = dp.get("context", "")

            # 根据上下文分类（简化版）
            if any(keyword in context for keyword in ["市场", "规模", "亿元"]):
                analysis_report["market_trends"]["market_size"].append({
                    "data": data,
                    "context": context,
                    "source": title,
                    "url": url
                })

            elif any(keyword in context for keyword in ["增长", "率", "%"]):
                analysis_report["market_trends"]["growth_rate"].append({
                    "data": data,
                    "context": context,
                    "source": title,
                    "url": url
                })

            elif any(keyword in context for keyword in ["ROI", "回报", "效益"]):
                analysis_report["business_value"]["roi_cases"].append({
                    "data": data,
                    "context": context,
                    "source": title,
                    "url": url
                })

            elif any(keyword in context for keyword in ["成本", "降低"]):
                analysis_report["business_value"]["cost_benefits"].append({
                    "data": data,
                    "context": context,
                    "source": title,
                    "url": url
                })

            elif any(keyword in context for keyword in ["效率", "提升"]):
                analysis_report["technology_innovation"]["efficiency_gains"].append({
                    "data": data,
                    "context": context,
                    "source": title,
                    "url": url
                })

            elif any(keyword in context for keyword in ["政策", "支持", "补贴"]):
                analysis_report["policy_environment"]["policy_supports"].append({
                    "data": data,
                    "context": context,
                    "source": title,
                    "url": url
                })

        # 提取案例（如果文章包含案例信息）
        if "案例" in title or "应用" in title or "实践" in title:
            analysis_report["case_studies"].append({
                "title": title,
                "url": url,
                "credibility_score": credibility_score,
                "data_points_count": len(data_points)
            })

    # 生成关键洞察（汇总）
    # 注意：实际使用时，Claude会基于以上分析生成关键洞察
    analysis_report["key_insights"] = [
        "市场持续增长，驱动因素明确",
        "技术应用带来显著效率提升",
        "政策环境支持行业发展",
        "投资回报周期合理"
    ]

    # 统计信息
    logger.info("\n内容分析完成：")
    logger.info(f"  市场规模数据点：{len(analysis_report['market_trends']['market_size'])}")
    logger.info(f"  增长率数据点：{len(analysis_report['market_trends']['growth_rate'])}")
    logger.info(f"  ROI案例：{len(analysis_report['business_value']['roi_cases'])}")
    logger.info(f"  成本效益案例：{len(analysis_report['business_value']['cost_benefits'])}")
    logger.info(f"  效率提升案例：{len(analysis_report['technology_innovation']['efficiency_gains'])}")
    logger.info(f"  政策支持数据点：{len(analysis_report['policy_environment']['policy_supports'])}")
    logger.info(f"  应用案例：{len(analysis_report['case_studies'])}")

    # 保存结果
    if save_json(analysis_report, output_path):
        logger.info(f"\n分析报告已保存：{output_path}")
        return True
    else:
        logger.error("保存分析报告失败")
        return False


def main():
    """主函数（用于测试）"""
    import argparse

    parser = argparse.ArgumentParser(description="内容分析模块 - 工程制造业文章创作器")
    parser.add_argument(
        '--input',
        required=True,
        type=Path,
        help='已验证的搜索结果文件路径'
    )
    parser.add_argument(
        '--output',
        required=True,
        type=Path,
        help='输出文件路径'
    )

    args = parser.parse_args()

    # 执行内容分析
    success = analyze_content_for_management(args.input, args.output)

    if success:
        logger.info("\n内容分析任务完成！")
        sys.exit(0)
    else:
        logger.error("\n内容分析任务失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
