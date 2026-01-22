"""
文章生成模块 - 工程制造业文章创作器

艹，老王我提醒你一下：
- 这个模块负责生成 Markdown 文章
- 必须应用管理层语言风格（聚焦商业价值、结论导向）
- 必须整合数据和引用（带完整来源追溯）
- 别tm乱改代码，会影响文章质量！
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# 添加scripts目录到Python路径（兼容Windows和Mac）
sys.path.insert(0, str(Path(__file__).parent))

from common import load_json, save_json, extract_domain, get_timestamp, get_credibility_level, logger


# =============================================================================
# 文章类型定义
# =============================================================================

ARTICLE_TYPES = {
    "industry_analysis": "行业分析报告",
    "tech_research": "技术研究文章",
    "case_study": "案例研究/应用",
    "feasibility_study": "可行性研究报告",
}


# =============================================================================
# 文章生成器类
# =============================================================================

class ArticleGenerator:
    """文章生成器类"""

    def __init__(self, analysis_report_path: Path, output_dir: Path):
        """
        初始化文章生成器

        Args:
            analysis_report_path: 内容分析报告路径（JSON）
            output_dir: 输出目录
        """
        self.analysis_report_path = analysis_report_path
        self.output_dir = output_dir
        self.analysis_report = None

        # 加载分析报告
        self._load_analysis_report()

    def _load_analysis_report(self) -> None:
        """加载内容分析报告"""
        logger.info(f"艹，正在加载分析报告：{self.analysis_report_path}")
        self.analysis_report = load_json(self.analysis_report_path)

        if not self.analysis_report:
            raise ValueError(f"艹，分析报告加载失败：{self.analysis_report_path}")

        logger.info("艹，分析报告加载成功")

    def generate(self, article_type: str) -> Path:
        """
        生成文章

        Args:
            article_type: 文章类型（industry_analysis、tech_research、case_study、feasibility_study）

        Returns:
            生成的文章文件路径
        """
        logger.info(f"艹，正在生成文章：{ARTICLE_TYPES.get(article_type, article_type)}")

        # 验证文章类型
        if article_type not in ARTICLE_TYPES:
            raise ValueError(f"艹，不支持的文章类型：{article_type}")

        # 生成文章内容
        content = self._generate_content(article_type)

        # 生成文件名
        filename = self._generate_filename(article_type)
        output_path = self.output_dir / filename

        # 写入文件
        output_path.write_text(content, encoding='utf-8')

        logger.info(f"艹，文章生成成功：{output_path}")

        return output_path

    def _generate_content(self, article_type: str) -> str:
        """
        生成文章内容

        Args:
            article_type: 文章类型

        Returns:
            文章内容（Markdown 格式）
        """
        # 根据文章类型选择生成方法
        if article_type == "industry_analysis":
            return self._generate_industry_analysis()
        elif article_type == "tech_research":
            return self._generate_tech_research()
        elif article_type == "case_study":
            return self._generate_case_study()
        elif article_type == "feasibility_study":
            return self._generate_feasibility_study()
        else:
            raise ValueError(f"艹，不支持的文章类型：{article_type}")

    def _generate_filename(self, article_type: str) -> str:
        """
        生成文件名

        Args:
            article_type: 文章类型

        Returns:
            文件名
        """
        topic = self.analysis_report.get('topic', '未命名主题')
        timestamp = datetime.now().strftime("%Y%m%d")

        # 清理主题中的非法字符
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()

        return f"{safe_topic}_{ARTICLE_TYPES[article_type]}_{timestamp}.md"

    # =============================================================================
    # 文章生成方法（按文章类型）
    # =============================================================================

    def _generate_industry_analysis(self) -> str:
        """
        生成行业分析报告

        Returns:
            文章内容（Markdown 格式）
        """
        logger.info("艹，正在生成行业分析报告")

        # 提取分析数据
        topic = self.analysis_report.get('topic', '')
        market_trends = self.analysis_report.get('market_trends', {})
        commercial_value = self.analysis_report.get('commercial_value', {})
        tech_innovation = self.analysis_report.get('tech_innovation', {})
        policy_environment = self.analysis_report.get('policy_environment', {})
        data_points = self.analysis_report.get('data_points', [])

        # 生成文章
        content = f"# {topic} - 行业分析报告\n\n"
        content += f"> **生成时间**：{get_timestamp()}\n\n"
        content += "---\n\n"

        # 一、市场现状
        content += "## 一、市场现状\n\n"

        if market_trends:
            content += "### 1.1 市场规模\n\n"
            content += self._format_data_points(market_trends.get('market_size', []), data_points)
            content += "\n"

            content += "### 1.2 增长趋势\n\n"
            content += self._format_data_points(market_trends.get('growth_rate', []), data_points)
            content += "\n"

            content += "### 1.3 驱动因素\n\n"
            content += self._format_list(market_trends.get('drivers', []))
            content += "\n"

        # 二、商业价值
        content += "## 二、商业价值\n\n"

        if commercial_value:
            content += "### 2.1 ROI 分析\n\n"
            content += self._format_data_points(commercial_value.get('roi', []), data_points)
            content += "\n"

            content += "### 2.2 成本效益\n\n"
            content += self._format_data_points(commercial_value.get('cost_benefit', []), data_points)
            content += "\n"

            content += "### 2.3 竞争优势\n\n"
            content += self._format_list(commercial_value.get('competitive_advantage', []))
            content += "\n"

        # 三、技术创新
        content += "## 三、技术创新\n\n"

        if tech_innovation:
            content += "### 3.1 技术突破\n\n"
            content += self._format_list(tech_innovation.get('breakthroughs', []))
            content += "\n"

            content += "### 3.2 应用场景\n\n"
            content += self._format_list(tech_innovation.get('applications', []))
            content += "\n"

            content += "### 3.3 效果评估\n\n"
            content += self._format_data_points(tech_innovation.get('effectiveness', []), data_points)
            content += "\n"

        # 四、政策环境
        content += "## 四、政策环境\n\n"

        if policy_environment:
            content += "### 4.1 政策支持\n\n"
            content += self._format_list(policy_environment.get('support', []))
            content += "\n"

            content += "### 4.2 监管要求\n\n"
            content += self._format_list(policy_environment.get('regulations', []))
            content += "\n"

        # 五、数据来源清单
        content += self._generate_data_sources_appendix(data_points)

        return content

    def _generate_tech_research(self) -> str:
        """
        生成技术研究文章

        Returns:
            文章内容（Markdown 格式）
        """
        logger.info("艹，正在生成技术研究文章")

        # 提取分析数据
        topic = self.analysis_report.get('topic', '')
        tech_innovation = self.analysis_report.get('tech_innovation', {})
        data_points = self.analysis_report.get('data_points', [])

        # 生成文章
        content = f"# {topic} - 技术研究\n\n"
        content += f"> **生成时间**：{get_timestamp()}\n\n"
        content += "---\n\n"

        # 一、技术背景
        content += "## 一、技术背景\n\n"
        content += self._format_paragraphs(tech_innovation.get('background', []))
        content += "\n"

        # 二、技术原理
        content += "## 二、技术原理\n\n"
        content += self._format_paragraphs(tech_innovation.get('principles', []))
        content += "\n"

        # 三、技术突破
        content += "## 三、技术突破\n\n"
        content += self._format_list(tech_innovation.get('breakthroughs', []))
        content += "\n"

        # 四、应用场景
        content += "## 四、应用场景\n\n"
        content += self._format_list(tech_innovation.get('applications', []))
        content += "\n"

        # 五、效果评估
        content += "## 五、效果评估\n\n"
        content += self._format_data_points(tech_innovation.get('effectiveness', []), data_points)
        content += "\n"

        # 六、数据来源清单
        content += self._generate_data_sources_appendix(data_points)

        return content

    def _generate_case_study(self) -> str:
        """
        生成案例研究/应用

        Returns:
            文章内容（Markdown 格式）
        """
        logger.info("艹，正在生成案例研究/应用")

        # 提取分析数据
        topic = self.analysis_report.get('topic', '')
        cases = self.analysis_report.get('cases', {})
        data_points = self.analysis_report.get('data_points', [])

        # 生成文章
        content = f"# {topic} - 案例研究\n\n"
        content += f"> **生成时间**：{get_timestamp()}\n\n"
        content += "---\n\n"

        # 一、案例背景
        content += "## 一、案例背景\n\n"
        content += self._format_paragraphs(cases.get('background', []))
        content += "\n"

        # 二、实施方案
        content += "## 二、实施方案\n\n"
        content += self._format_paragraphs(cases.get('implementation', []))
        content += "\n"

        # 三、实施效果
        content += "## 三、实施效果\n\n"
        content += self._format_data_points(cases.get('results', []), data_points)
        content += "\n"

        # 四、经验总结
        content += "## 四、经验总结\n\n"
        content += self._format_list(cases.get('lessons', []))
        content += "\n"

        # 五、数据来源清单
        content += self._generate_data_sources_appendix(data_points)

        return content

    def _generate_feasibility_study(self) -> str:
        """
        生成可行性研究报告

        Returns:
            文章内容（Markdown 格式）
        """
        logger.info("艹，正在生成可行性研究报告")

        # 提取分析数据
        topic = self.analysis_report.get('topic', '')
        company = self.analysis_report.get('company', {})
        market_trends = self.analysis_report.get('market_trends', {})
        commercial_value = self.analysis_report.get('commercial_value', {})
        policy_environment = self.analysis_report.get('policy_environment', {})
        data_points = self.analysis_report.get('data_points', [])

        # 生成文章
        content = f"# {topic} - 可行性研究报告\n\n"
        content += f"> **生成时间**：{get_timestamp()}\n\n"
        content += "---\n\n"

        # 一、项目背景
        content += "## 一、项目背景\n\n"

        if company:
            content += f"### 1.1 主体公司\n\n"
            content += f"**公司名称**：{company.get('name', '')}\n\n"
            content += f"**行业地位**：{company.get('position', '')}\n\n"
            content += f"**核心优势**：{', '.join(company.get('strengths', []))}\n\n"
            content += "\n"

        # 二、市场分析
        content += "## 二、市场分析\n\n"

        if market_trends:
            content += "### 2.1 市场规模\n\n"
            content += self._format_data_points(market_trends.get('market_size', []), data_points)
            content += "\n"

            content += "### 2.2 增长趋势\n\n"
            content += self._format_data_points(market_trends.get('growth_rate', []), data_points)
            content += "\n"

        # 三、商业价值
        content += "## 三、商业价值\n\n"

        if commercial_value:
            content += "### 3.1 ROI 分析\n\n"
            content += self._format_data_points(commercial_value.get('roi', []), data_points)
            content += "\n"

            content += "### 3.2 投资回报期\n\n"
            content += self._format_data_points(commercial_value.get('payback_period', []), data_points)
            content += "\n"

        # 四、政策环境
        content += "## 四、政策环境\n\n"

        if policy_environment:
            content += "### 4.1 政策支持\n\n"
            content += self._format_list(policy_environment.get('support', []))
            content += "\n"

            content += "### 4.2 监管要求\n\n"
            content += self._format_list(policy_environment.get('regulations', []))
            content += "\n"

        # 五、可行性结论
        content += "## 五、可行性结论\n\n"

        # 计算可行性评分
        feasibility_score = self._calculate_feasibility_score(
            market_trends, commercial_value, policy_environment
        )

        content += f"**可行性评分**：{feasibility_score}/10\n\n"
        content += self._format_feasibility_conclusion(feasibility_score)
        content += "\n"

        # 六、数据来源清单
        content += self._generate_data_sources_appendix(data_points)

        return content

    # =============================================================================
    # 辅助方法
    # =============================================================================

    def _format_data_points(self, items: List[Any], data_points: List[Dict]) -> str:
        """
        格式化数据点（带脚注）

        Args:
            items: 数据项列表
            data_points: 所有数据点（用于查找来源）

        Returns:
            格式化后的文本
        """
        if not items:
            return ""

        content = ""

        for i, item in enumerate(items, 1):
            if isinstance(item, dict):
                text = item.get('text', str(item))
                source_url = item.get('source_url', '')

                # 查找对应的数据点
                footnote = self._find_footnote(source_url, data_points)

                content += f"{i}. {text}{footnote}\n"
            else:
                content += f"{i}. {item}\n"

        return content

    def _find_footnote(self, source_url: str, data_points: List[Dict]) -> str:
        """
        查找数据点的脚注

        Args:
            source_url: 来源 URL
            data_points: 所有数据点

        Returns:
            脚注（例如：[^1]）
        """
        if not source_url or not data_points:
            return ""

        for i, dp in enumerate(data_points, 1):
            if dp.get('source_url') == source_url:
                return f"[^{i}]"

        return ""

    def _format_list(self, items: List[str]) -> str:
        """
        格式化列表

        Args:
            items: 列表项

        Returns:
            格式化后的文本
        """
        if not items:
            return ""

        content = ""

        for item in items:
            content += f"- {item}\n"

        return content

    def _format_paragraphs(self, items: List[str]) -> str:
        """
        格式化段落

        Args:
            items: 段落列表

        Returns:
            格式化后的文本
        """
        if not items:
            return ""

        content = ""

        for item in items:
            content += f"{item}\n\n"

        return content

    def _calculate_feasibility_score(self, market_trends: Dict,
                                     commercial_value: Dict,
                                     policy_environment: Dict) -> float:
        """
        计算可行性评分

        Args:
            market_trends: 市场趋势数据
            commercial_value: 商业价值数据
            policy_environment: 政策环境数据

        Returns:
            可行性评分（0-10分）
        """
        score = 0.0

        # 市场前景（0-4分）
        if market_trends.get('market_size'):
            score += 2.0
        if market_trends.get('growth_rate'):
            score += 2.0

        # 商业价值（0-4分）
        if commercial_value.get('roi'):
            score += 2.0
        if commercial_value.get('payback_period'):
            score += 2.0

        # 政策支持（0-2分）
        if policy_environment.get('support'):
            score += 2.0

        return min(score, 10.0)

    def _format_feasibility_conclusion(self, score: float) -> str:
        """
        格式化可行性结论

        Args:
            score: 可行性评分

        Returns:
            结论文本
        """
        if score >= 8.0:
            return "**结论**：项目可行性极高，建议立即启动实施。\n\n"
        if score >= 6.0:
            return "**结论**：项目可行性较高，建议进一步调研后启动实施。\n\n"
        if score >= 4.0:
            return "**结论**：项目可行性一般，建议深入分析风险后再做决策。\n\n"
        return "**结论**：项目可行性较低，建议谨慎考虑或暂缓实施。\n\n"

    def _generate_data_sources_appendix(self, data_points: List[Dict]) -> str:
        """
        生成数据来源清单附录

        Args:
            data_points: 所有数据点

        Returns:
            数据来源清单（Markdown 格式）
        """
        if not data_points:
            return ""

        content = "\n---\n\n"
        content += "## 附录：完整数据来源清单\n\n"

        # 按类别分组
        categories = {}
        for i, dp in enumerate(data_points, 1):
            category = dp.get('category', '其他')
            if category not in categories:
                categories[category] = []
            categories[category].append((i, dp))

        # 生成分类表格
        for category, items in categories.items():
            content += f"### {category}\n\n"
            content += "| 数据点 | 数值 | 来源 | URL | 访问时间 |\n"
            content += "|--------|------|------|-----|----------|\n"

            for i, dp in items:
                data = dp.get('data', '')
                value = dp.get('value', '')
                source = dp.get('source_title', dp.get('source', ''))
                url = dp.get('source_url', '')
                access_time = dp.get('access_time', '')

                content += f"| {data} | {value} | {source} | {url} | {access_time} |\n"

            content += "\n"

        # 生成脚注列表
        content += "### 脚注\n\n"
        for i, dp in enumerate(data_points, 1):
            source = dp.get('source_title', dp.get('source', ''))
            url = dp.get('source_url', '')
            access_time = dp.get('access_time', '')

            content += f"[^{i}]: 数据来源：{source}，{url}，访问时间：{access_time}\n"

        content += "\n"

        # 生成数据质量说明
        content += "### 数据质量说明\n\n"

        total = len(data_points)
        verified = sum(1 for dp in data_points if dp.get('verified', False))
        verification_rate = (verified / total * 100) if total > 0 else 0

        content += f"- 总数据点：**{total}个**\n"
        content += f"- 已验证来源：**{verified}个**（{verification_rate:.1f}%）\n"

        # 按可信度分类
        credibility_levels = {}
        for dp in data_points:
            score = dp.get('credibility_score', 0)
            level = get_credibility_level(score)
            credibility_levels[level] = credibility_levels.get(level, 0) + 1

        content += "\n**来源可信度评分**：\n"
        for level, count in sorted(credibility_levels.items(), key=lambda x: -x[1]):
            content += f"- {level}：**{count}个**\n"

        return content


# =============================================================================
# 主函数
# =============================================================================

def main():
    """主函数（用于测试）"""
    # 测试代码
    pass


if __name__ == "__main__":
    main()
