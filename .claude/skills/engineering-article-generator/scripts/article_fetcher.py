"""
全文爬取模块 - 工程制造业文章创作器
批量爬取文章全文内容，提取元数据
"""

import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加scripts目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from common import logger, load_json, save_json


def fetch_article_content(url: str, use_mcp: bool = True) -> Dict[str, Any]:
    """
    爬取单篇文章的全文内容

    注意：这是一个框架函数，实际使用时需要通过Claude Code调用MCP工具

    Args:
        url: 文章URL
        use_mcp: 是否使用MCP工具（推荐）

    Returns:
        文章数据字典（包含content、title、author、publish_date等）
    """
    logger.info(f"爬取文章：{url}")

    # 注意：实际使用时会通过Claude Code调用MCP工具
    #
    # 推荐方式：使用 web_reader MCP工具
    # result = mcp__web_reader__webReader(
    #     url=url,
    #     return_format="markdown"
    # )
    #
    # 或者使用 web-reader MCP工具（另一个）
    # result = mcp__web-reader__webReader(
    #     url=url,
    #     return_format="markdown"
    # )

    # 返回模拟数据（实际使用时会替换为真实数据）
    return {
        "url": url,
        "title": "模拟文章标题",
        "content": "这是模拟的文章正文内容...",
        "author": "模拟作者",
        "publish_date": "2025-06-15",
        "images": [],
        "fetched_at": datetime.now().isoformat(),
        "fetch_success": True
    }


def fetch_articles_batch(deduped_results_path: Path, output_path: Path, max_articles: int = 15) -> bool:
    """
    批量爬取文章全文内容

    Args:
        deduped_results_path: 去重后的搜索结果文件路径
        output_path: 输出文件路径
        max_articles: 最多爬取文章数（默认15篇，按质量评分从高到低）

    Returns:
        是否执行成功
    """
    # 加载去重后的搜索结果
    deduped_data = load_json(deduped_results_path)
    if not deduped_data:
        logger.error("加载去重结果失败")
        return False

    articles = deduped_data.get("results", [])
    logger.info(f"加载了 {len(articles)} 篇去重后的文章")

    logger.info("=" * 80)
    logger.info("开始批量爬取文章全文")
    logger.info("=" * 80)

    # 按质量评分排序，取前N篇
    sorted_articles = sorted(
        articles,
        key=lambda x: x.get("credibility_score", 0),
        reverse=True
    )[:max_articles]

    logger.info(f"将爬取前 {len(sorted_articles)} 篇高质量文章的全文内容")

    # 批量爬取
    fetched_articles = []
    success_count = 0
    fail_count = 0

    for i, article in enumerate(sorted_articles, 1):
        url = article.get("url", "")
        logger.info(f"\n[{i}/{len(sorted_articles)}] 爬取：{url}")

        # 注意：实际使用时会通过Claude Code调用MCP web_reader工具
        # 这里提供示例代码供参考
        #
        # 方式1：使用 web_reader
        # try:
        #     result = mcp__web_reader__webReader(
        #         url=url,
        #         return_format="markdown",
        #         retain_images=False,
        #         timeout=20
        #     )
        #     # 解析result，提取content、title等
        #     article_data = {
        #         "url": url,
        #         "title": result.get("title", article.get("title", "")),
        #         "content": result.get("content", ""),
        #         "author": result.get("author", ""),
        #         "publish_date": result.get("publish_date", article.get("publish_date", "")),
        #         "fetched_at": datetime.now().isoformat(),
        #         "fetch_success": True
        #     }
        #     success_count += 1
        # except Exception as e:
        #     logger.error(f"爬取失败：{e}")
        #     article_data = {
        #         "url": url,
        #         "error": str(e),
        #         "fetched_at": datetime.now().isoformat(),
        #         "fetch_success": False
        #     }
        #     fail_count += 1
        #
        # 方式2：使用 requests + BeautifulSoup（备用）
        # import requests
        # from bs4 import BeautifulSoup
        #
        # try:
        #     headers = {
        #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        #     }
        #     response = requests.get(url, headers=headers, timeout=10)
        #     response.raise_for_status()
        #
        #     soup = BeautifulSoup(response.text, 'html.parser')
        #
        #     # 智能识别文章正文
        #     content_selectors = [
        #         'article',
        #         '[class*="content"]',
        #         '[class*="article"]',
        #         'main'
        #     ]
        #
        #     content_elem = None
        #     for selector in content_selectors:
        #         content_elem = soup.select_one(selector)
        #         if content_elem:
        #             break
        #
        #     content = content_elem.get_text(strip=True) if content_elem else ""
        #
        #     article_data = {
        #         "url": url,
        #         "title": soup.title.string if soup.title else "",
        #         "content": content,
        #         "fetched_at": datetime.now().isoformat(),
        #         "fetch_success": True
        #     }
        #     success_count += 1
        # except Exception as e:
        #     logger.error(f"爬取失败：{e}")
        #     fail_count += 1

        logger.warning("注意：这是模拟函数，实际使用时需要通过Claude Code调用MCP web_reader工具")

        # 模拟数据（实际使用时删除）
        article_data = {
            "url": url,
            "title": article.get("title", ""),
            "content": f"这是从 {url} 爬取的模拟文章正文内容..." * 10,  # 模拟长文
            "author": "模拟作者",
            "publish_date": article.get("publish_date", ""),
            "credibility_score": article.get("credibility_score", 0),
            "dimension": article.get("dimension", ""),
            "fetched_at": datetime.now().isoformat(),
            "fetch_success": True
        }

        fetched_articles.append(article_data)

        # 添加延迟，避免请求过快
        time.sleep(1)

    # 汇总结果
    output_data = {
        "task_id": deduped_data.get("task_id", ""),
        "total_articles": len(sorted_articles),
        "successfully_fetched": success_count,
        "failed_to_fetch": fail_count,
        "articles": fetched_articles,
        "fetch_completed_at": datetime.now().isoformat()
    }

    # 保存结果
    if save_json(output_data, output_path):
        logger.info(f"\n全文内容已保存：{output_path}")
        logger.info(f"成功爬取：{success_count} 篇")
        logger.info(f"爬取失败：{fail_count} 篇")
        return True
    else:
        logger.error("保存全文内容失败")
        return False


def main():
    """主函数（用于测试）"""
    import argparse

    parser = argparse.ArgumentParser(description="全文爬取模块 - 工程制造业文章创作器")
    parser.add_argument(
        '--input',
        required=True,
        type=Path,
        help='去重后的搜索结果文件路径'
    )
    parser.add_argument(
        '--output',
        required=True,
        type=Path,
        help='输出文件路径'
    )
    parser.add_argument(
        '--max-articles',
        type=int,
        default=15,
        help='最多爬取文章数（默认15篇）'
    )

    args = parser.parse_args()

    # 执行批量爬取
    success = fetch_articles_batch(args.input, args.output, args.max_articles)

    if success:
        logger.info("\n全文爬取任务完成！")
        sys.exit(0)
    else:
        logger.error("\n全文爬取任务失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
