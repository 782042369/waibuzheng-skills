"""
去重模块 - 工程制造业文章创作器
汇总搜索结果并去重、质量排序
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict

# 添加scripts目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from common import logger, load_json, save_json, normalize_url, calculate_credibility_score, get_credibility_level


def deduplicate_search_results(search_results_path: Path, output_path: Path) -> bool:
    """
    汇总搜索结果并去重

    Args:
        search_results_path: 搜索结果文件路径
        output_path: 输出文件路径

    Returns:
        是否执行成功
    """
    # 加载搜索结果
    search_data = load_json(search_results_path)
    if not search_data:
        logger.error("加载搜索结果失败")
        return False

    results = search_data.get("results", [])
    logger.info(f"加载了 {len(results)} 条搜索结果")

    logger.info("=" * 80)
    logger.info("开始去重和质量排序")
    logger.info("=" * 80)

    # 去重（基于标准化URL）
    unique_articles = {}
    duplicate_count = 0

    for article in results:
        url = article.get("url", "")
        if not url:
            continue

        normalized_url = normalize_url(url)

        if normalized_url not in unique_articles:
            # 首次出现，直接添加
            unique_articles[normalized_url] = article
        else:
            # 重复URL，保留质量更高的（优先保留有content的）
            existing = unique_articles[normalized_url]
            if "content" in article and "content" not in existing:
                unique_articles[normalized_url] = article
                duplicate_count += 1
            else:
                duplicate_count += 1

    deduped_results = list(unique_articles.values())
    logger.info(f"去重后剩余 {len(deduped_results)} 篇文章（移除 {duplicate_count} 篇重复）")

    # 质量评分和排序
    logger.info("\n开始质量评分...")

    for article in deduped_results:
        # 计算可信度评分
        article["credibility_score"] = calculate_credibility_score(article)

    # 按质量评分排序（从高到低）
    deduped_results.sort(key=lambda x: x.get("credibility_score", 0), reverse=True)

    # 统计质量分布
    quality_stats = defaultdict(int)
    for article in deduped_results:
        score = article.get("credibility_score", 0)
        level = get_credibility_level(score)
        quality_stats[level] += 1

    logger.info("\n质量评分分布：")
    for level, count in sorted(quality_stats.items(), key=lambda x: x[1], reverse=True):
        logger.info(f"  {level}：{count} 篇")

    # 确保至少保留10篇高质量文章（评分 >= 5.0分）
    high_quality_articles = [a for a in deduped_results if a.get("credibility_score", 0) >= 5.0]
    logger.info(f"\n高质量文章（评分 >= 5.0）：{len(high_quality_articles)} 篇")

    if len(high_quality_articles) < 10:
        logger.warning(f"高质量文章不足10篇，当前仅 {len(high_quality_articles)} 篇")
        logger.warning("建议：扩展搜索范围或调整搜索查询")

    # 构建输出数据
    output_data = {
        "task_id": search_data.get("task_id", ""),
        "total_original_results": len(results),
        "total_deduped_results": len(deduped_results),
        "duplicates_removed": duplicate_count,
        "quality_distribution": dict(quality_stats),
        "high_quality_count": len(high_quality_articles),
        "results": deduped_results,
        "deduplication_completed_at": datetime.now().isoformat()
    }

    # 保存结果
    if save_json(output_data, output_path):
        logger.info(f"\n去重结果已保存：{output_path}")
        return True
    else:
        logger.error("保存去重结果失败")
        return False


def main():
    """主函数（用于测试）"""
    import argparse

    parser = argparse.ArgumentParser(description="去重模块 - 工程制造业文章创作器")
    parser.add_argument(
        '--input',
        required=True,
        type=Path,
        help='搜索结果文件路径'
    )
    parser.add_argument(
        '--output',
        required=True,
        type=Path,
        help='输出文件路径'
    )

    args = parser.parse_args()

    # 执行去重
    success = deduplicate_search_results(args.input, args.output)

    if success:
        logger.info("\n去重任务完成！")
        sys.exit(0)
    else:
        logger.error("\n去重任务失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
