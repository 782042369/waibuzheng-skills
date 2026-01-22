"""
公共工具模块 - 工程制造业文章创作器
提供通用的工具函数和类
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import urllib.parse


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JSONEncoder(json.JSONEncoder):
    """自定义JSON编码器，处理datetime等特殊类型"""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Path):
            return str(obj)
        return super().default(obj)


def load_json(file_path: Path) -> Dict[str, Any]:
    """
    加载JSON文件

    Args:
        file_path: JSON文件路径

    Returns:
        解析后的JSON数据
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载JSON文件失败: {file_path}, 错误: {e}")
        return {}


def save_json(data: Dict[str, Any], file_path: Path) -> bool:
    """
    保存JSON文件

    Args:
        data: 要保存的数据
        file_path: 保存路径

    Returns:
        是否保存成功
    """
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, cls=JSONEncoder)
        logger.info(f"JSON文件保存成功: {file_path}")
        return True
    except Exception as e:
        logger.error(f"保存JSON文件失败: {file_path}, 错误: {e}")
        return False


def normalize_url(url: str) -> str:
    """
    标准化URL（用于去重）

    Args:
        url: 原始URL

    Returns:
        标准化后的URL
    """
    try:
        # 解析URL
        parsed = urllib.parse.urlparse(url)

        # 移除常见的跟踪参数
        query_params = urllib.parse.parse_qs(parsed.query)
        tracking_params = {'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
                          'fbclid', 'gclid', 'msclkid'}

        # 过滤掉跟踪参数
        filtered_params = {k: v for k, v in query_params.items() if k not in tracking_params}

        # 重建URL
        new_query = urllib.parse.urlencode(filtered_params, doseq=True)
        normalized = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc.lower(),  # 域名转小写
            parsed.path,
            parsed.params,
            new_query,
            ''  # 移除fragment
        ))

        return normalized
    except Exception as e:
        logger.warning(f"URL标准化失败: {url}, 错误: {e}")
        return url


def extract_domain(url: str) -> str:
    """
    从URL中提取域名

    Args:
        url: URL字符串

    Returns:
        域名
    """
    try:
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc.lower()
    except Exception as e:
        logger.warning(f"提取域名失败: {url}, 错误: {e}")
        return ""


def calculate_credibility_score(article: Dict[str, Any]) -> float:
    """
    计算文章来源的可信度评分（0-10分）

    评分标准：
    1. 来源权威性（0-4分）
    2. 内容完整性（0-3分）
    3. 数据支撑（0-2分）
    4. 时效性（0-1分）

    Args:
        article: 文章数据字典

    Returns:
        可信度评分（0-10分）
    """
    score = 0.0

    # 1. 来源权威性（0-4分）
    domain = extract_domain(article.get('url', ''))
    authoritative_domains = {
        # 政府机构
        'gov.cn': 4.0,
        'miit.gov.cn': 4.0,
        'ndrc.gov.cn': 4.0,
        # 行业协会
        'ccma.org.cn': 4.0,
        'cmca.org.cn': 4.0,
        # 专业媒体
        'd1cm.com': 3.0,
        'cm.365sme.com': 3.0,
        'iresearch.com.cn': 3.0,
        'analysys.cn': 3.0,
    }

    authority_score = 1.0  # 默认分数
    for auth_domain, auth_score in authoritative_domains.items():
        if auth_domain in domain:
            authority_score = auth_score
            break
    score += authority_score

    # 2. 内容完整性（0-3分）
    content_length = len(article.get('content', ''))
    if content_length > 1000:
        score += 3.0
    elif content_length > 500:
        score += 2.0
    else:
        score += 1.0

    # 3. 数据支撑（0-2分）
    content = article.get('content', '')
    # 检查是否包含数据（数字、百分比等）
    has_data = any(char.isdigit() for char in content)
    if has_data:
        score += 2.0

    # 4. 时效性（0-1分）
    publish_date = article.get('publish_date', '')
    if publish_date:
        try:
            pub_datetime = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
            days_ago = (datetime.now(pub_datetime.tzinfo) - pub_datetime).days
            if days_ago <= 180:  # 最近6个月
                score += 1.0
            elif days_ago <= 365:  # 6-12个月
                score += 0.8
            elif days_ago <= 730:  # 12-24个月
                score += 0.5
        except:
            pass

    return min(score, 10.0)  # 最高10分


def get_credibility_level(score: float) -> str:
    """
    根据可信度评分返回等级

    Args:
        score: 可信度评分

    Returns:
        可信度等级（极高、高、中、低）
    """
    if score >= 9.0:
        return "极高"
    if score >= 7.0:
        return "高"
    if score >= 5.0:
        return "中"
    return "低"


def create_output_directory(base_path: Path, topic: str) -> Path:
    """
    创建输出目录

    Args:
        base_path: 基础路径
        topic: 主题

    Returns:
        输出目录路径
    """
    # 清理主题中的非法字符
    safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = base_path / f"{safe_topic}_{timestamp}"

    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"创建输出目录: {output_dir}")

    return output_dir


def get_timestamp() -> str:
    """
    获取当前时间戳字符串

    Returns:
        ISO 格式的时间戳
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    # 测试代码
    test_url = "https://example.com/test?utm_source=google&utm_medium=cpc&id=123"
    normalized = normalize_url(test_url)
    print(f"原始URL: {test_url}")
    print(f"标准化URL: {normalized}")
    print(f"域名: {extract_domain(normalized)}")
