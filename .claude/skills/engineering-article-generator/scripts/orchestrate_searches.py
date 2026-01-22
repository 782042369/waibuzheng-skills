"""
编排脚本 - 工程制造业文章创作器
负责参数验证、生成搜索任务配置、生成Claude Code调用说明
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加scripts目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from common import logger, save_json, create_output_directory


# 支持的文章类型
ARTICLE_TYPES = [
    "industry_analysis",  # 行业分析报告
    "tech_research",      # 技术研究文章
    "case_study",         # 案例研究/应用
    "feasibility_study"   # 可行性研究报告
]

# 支持的搜索维度
DIMENSIONS = [
    "company",    # 公司层面
    "industry",   # 行业层面
    "china",      # 全国层面
    "global",     # 全球层面
    "media",      # 媒体报道
    "influencer", # 从业者观点
    "policy"      # 政策环境
]


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="工程制造业文章创作器 - 编排脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：

  行业分析报告：
  python orchestrate_searches.py \\
    --topic "工程机械智能化" \\
    --article-type industry_analysis \\
    --company "三一重工" \\
    --industry "工程机械" \\
    --dimensions "company,industry,china,global,media" \\
    --output "./output"

  可行性研究报告（Windows路径示例）：
  python orchestrate_searches.py \\
    --topic "工程机械和重型机械再制造" \\
    --article-type feasibility_study \\
    --company "太重集团" \\
    --industry "工程机械" \\
    --dimensions "company,global,policy,media" \\
    --output "E:/articles/output"

注意：
  - Windows 路径可用正斜杠 / 或双反斜杠 \\\\
  - Mac/Linux 路径使用正斜杠 /
        """
    )

    # 必需参数
    parser.add_argument(
        '--topic',
        required=True,
        help='文章主题（例如："工程机械智能化"）'
    )

    parser.add_argument(
        '--article-type',
        required=True,
        choices=ARTICLE_TYPES,
        help='文章类型'
    )

    # 可选参数
    parser.add_argument(
        '--company',
        help='目标公司（例如："三一重工"）'
    )

    parser.add_argument(
        '--industry',
        help='所属行业（例如："工程机械"）'
    )

    parser.add_argument(
        '--dimensions',
        default='company,industry,china,global,media',
        help=f'搜索维度，逗号分隔（默认：company,industry,china,global,media）。可选：{",".join(DIMENSIONS)}'
    )

    parser.add_argument(
        '--output',
        default=Path.cwd() / "output",
        type=Path,
        help='输出目录路径（默认：当前目录/output）'
    )

    return parser.parse_args()


def validate_arguments(args) -> bool:
    """
    验证参数的合理性

    Args:
        args: 命令行参数

    Returns:
        是否验证通过
    """
    # 验证文章类型和搜索维度的匹配
    if args.article_type == "feasibility_study":
        # 可行性研究必须包含company和global维度
        required_dims = {'company', 'global'}
        selected_dims = set(args.dimensions.split(','))
        missing_dims = required_dims - selected_dims
        if missing_dims:
            logger.error(f"可行性研究必须包含以下维度：{', '.join(missing_dims)}")
            return False

    # 验证输出目录
    if not args.output.parent.exists():
        logger.error(f"输出目录的父目录不存在：{args.output.parent}")
        return False

    return True


def generate_search_task_config(args, output_dir: Path) -> Path:
    """
    生成搜索任务配置文件（JSON格式）

    Args:
        args: 命令行参数
        output_dir: 输出目录

    Returns:
        配置文件路径
    """
    # 解析搜索维度
    dimensions_list = [d.strip() for d in args.dimensions.split(',')]

    # 构建搜索任务配置
    config = {
        "task_id": f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "created_at": datetime.now().isoformat(),
        "topic": args.topic,
        "article_type": args.article_type,
        "company": args.company or "",
        "industry": args.industry or "",
        "dimensions": dimensions_list,
        "output_dir": str(output_dir),
        "search_time_range": {
            "start": "2024-01-22",
            "end": "2026-01-22"
        },
        "quality_requirements": {
            "min_verification_rate": 0.95,  # URL验证率必须 >= 95%
            "min_credibility_score": 5.0,   # 最低可信度评分
            "min_high_quality_articles": 10  # 至少保留10篇高质量文章
        }
    }

    # 保存配置文件
    config_path = output_dir / "tmp" / "search_task.json"
    save_json(config, config_path)

    return config_path


def generate_claude_instruction(args, output_dir: Path, config_path: Path) -> Path:
    """
    生成Claude Code调用说明（Markdown格式）

    Args:
        args: 命令行参数
        output_dir: 输出目录
        config_path: 配置文件路径

    Returns:
        调用说明文件路径
    """
    # 文章类型映射
    article_type_names = {
        "industry_analysis": "行业分析报告",
        "tech_research": "技术研究文章",
        "case_study": "案例研究/应用",
        "feasibility_study": "可行性研究报告"
    }

    # 维度映射
    dimension_names = {
        "company": "公司层面",
        "industry": "行业层面",
        "china": "全国层面",
        "global": "全球层面",
        "media": "媒体报道",
        "influencer": "从业者观点",
        "policy": "政策环境"
    }

    dimensions_list = [d.strip() for d in args.dimensions.split(',')]
    dimension_desc = ", ".join([dimension_names.get(d, d) for d in dimensions_list])

    instruction = f"""# 工程制造业文章创作器 - Claude Code 调用说明

## 任务概述

**文章主题**：{args.topic}
**文章类型**：{article_type_names[args.article_type]}
**目标公司**：{args.company or "未指定"}
**所属行业**：{args.industry or "未指定"}
**搜索维度**：{dimension_desc}

## 工作流程

### Step 1: 读取配置和参考文档

1. 读取搜索任务配置：`{config_path}`
2. 读取参考文档（根据需要加载）：
   - `references/workflow.md` - 完整工作流程
   - `references/data-validation-rules.md` - 数据验证规则
   - `references/article-prompts.md` - 文章类型模板
   - `references/tone-guide.md` - 管理层语言风格指南

### Step 2: 创建任务清单（TodoWrite）

使用以下任务步骤：

```python
TodoWrite([
    {{"content": "读取配置和参考文档", "status": "in_progress"}},
    {{"content": "启动搜索执行子智能体（{len(dimensions_list)}个维度）", "status": "pending"}},
    {{"content": "启动去重和全文爬取子智能体", "status": "pending"}},
    {{"content": "启动数据验证子智能体（关键）", "status": "pending"}},
    {{"content": "启动内容分析子智能体", "status": "pending"}},
    {{"content": "启动文章生成子智能体", "status": "pending"}},
    {{"content": "汇总结果并清理临时文件", "status": "pending"}}
])
```

### Step 3: 启动5个子智能体

#### 子智能体1：搜索执行者

**任务**：调用 `scripts/web_searcher.py` 执行{len(dimensions_list)}个维度的搜索
**输入**：搜索任务配置文件
**输出**：`{output_dir}/tmp/search_results.json`

**关键要求**：
- 每个搜索结果必须记录完整来源信息（URL、标题、摘要、发布日期、访问时间）
- 搜索查询必须优化（添加年份关键词、行业关键词、公司关键词）
- 限制搜索时间范围（最近两年）

#### 子智能体2：去重和全文爬取

**任务**：汇总搜索结果、去重、质量排序、批量爬取全文
**输入**：搜索结果JSON文件
**输出**：
- `{output_dir}/tmp/deduped_results.json` - 去重后的搜索结果
- `{output_dir}/tmp/fetched_articles.json` - 全文内容

**关键要求**：
- 必须确保至少保留 10-15 篇高质量文章（评分 >= 5.0分）
- 必须记录完整的元数据（标题、作者、发布日期、URL、爬取时间）

#### 子智能体3：数据验证者（**最关键**）

**任务**：验证所有URL、计算可信度评分、提取数据点、生成数据来源清单
**输入**：全文内容JSON文件
**输出**：`{output_dir}/tmp/validated_results.json`

**关键要求**：
- URL验证率必须 >= 95%（已验证URL / 总URL）
- 所有数据点必须标注完整来源（URL + 访问时间）
- 关键数据点必须人工审核（财务数据、市场数据）

**数据验证流程**：
1. URL验证（可访问性检查，返回200状态码）
2. 可信度评分（权威机构、专业媒体、公司官网）
3. 数据点提取（AI提取 + 人工审核）
4. 生成数据来源清单（按来源类型、可信度分类）

#### 子智能体4：内容分析者

**任务**：分析已验证的搜索结果，提取关键信息
**输入**：已验证的搜索结果JSON文件
**输出**：`{output_dir}/tmp/analysis_report.json`

**关键要求**：
- 只使用已验证的数据（verified=true）
- 聚焦商业价值（避免技术细节）
- 必须使用数据支撑论点（每个论点必须有数据来源）

#### 子智能体5：文章生成者

**任务**：根据文章类型生成Markdown文章
**输入**：内容分析报告JSON文件
**输出**：`{output_dir}/{args.topic}.md`

**关键要求**：
- 文章中每个数据点必须标注脚注[^1][^2]...
- 文章末尾生成"附录：完整数据来源清单"（表格格式）
- 文章包含"数据质量说明"（总数据点、已验证比例、来源分布、可信度评分）

### Step 4: 质量验收

**数据验证和来源追溯验收**：
- ✅ URL验证率必须 >= 95%
- ✅ 所有数据点必须标注完整来源
- ✅ 文章中每个数据点必须标注脚注
- ✅ 文章末尾生成"完整数据来源清单"
- ✅ 文章包含"数据质量说明"

**内容质量验收**：
- ✅ 文章聚焦商业价值和投资回报
- ✅ 文章结构清晰、逻辑连贯
- ✅ 数据和案例有明确来源和追溯路径

## 配置文件位置

- 搜索任务配置：`{config_path}`
- 输出目录：`{output_dir}`

## 注意事项

1. **数据真实性是核心**：所有数据必须真实可验证，不允许AI幻觉
2. **严格遵循数据验证规则**：参考 `references/data-validation-rules.md`
3. **管理层语言风格**：参考 `references/tone-guide.md`
4. **文章类型模板**：参考 `references/article-prompts.md`

## 临时文件结构

```
{output_dir}/tmp/
├── search_task.json              # 搜索任务配置
├── search_results.json           # 搜索结果
├── deduped_results.json          # 去重后的搜索结果
├── fetched_articles.json         # 全文内容
├── validated_results.json        # 已验证的搜索结果（带数据点）
├── analysis_report.json          # 结构化的分析报告
└── claude_instruction.md         # 本文件
```

---

**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    # 保存调用说明
    instruction_path = output_dir / "tmp" / "claude_instruction.md"
    instruction_path.parent.mkdir(parents=True, exist_ok=True)

    with open(instruction_path, 'w', encoding='utf-8') as f:
        f.write(instruction)

    logger.info(f"Claude Code调用说明已生成：{instruction_path}")

    return instruction_path


def main():
    """主函数"""
    # 解析参数
    args = parse_arguments()

    logger.info("=" * 80)
    logger.info("工程制造业文章创作器 - 编排脚本")
    logger.info("=" * 80)
    logger.info(f"文章主题：{args.topic}")
    logger.info(f"文章类型：{args.article_type}")
    logger.info(f"目标公司：{args.company or '未指定'}")
    logger.info(f"所属行业：{args.industry or '未指定'}")
    logger.info(f"搜索维度：{args.dimensions}")
    logger.info(f"输出目录：{args.output}")
    logger.info("=" * 80)

    # 验证参数
    if not validate_arguments(args):
        logger.error("参数验证失败，请检查输入")
        sys.exit(1)

    # 创建输出目录
    output_dir = create_output_directory(args.output, args.topic)
    logger.info(f"输出目录已创建：{output_dir}")

    # 生成搜索任务配置
    config_path = generate_search_task_config(args, output_dir)
    logger.info(f"搜索任务配置已生成：{config_path}")

    # 生成Claude Code调用说明
    instruction_path = generate_claude_instruction(args, output_dir, config_path)
    logger.info(f"Claude Code调用说明已生成：{instruction_path}")

    # 二次确认
    print("\n" + "=" * 80)
    print("配置文件生成成功！")
    print("=" * 80)
    print(f"\n输出目录：{output_dir}")
    print(f"配置文件：{config_path}")
    print(f"调用说明：{instruction_path}")
    print("\n下一步：")
    print("1. 阅读 Claude Code 调用说明：{instruction_path}")
    print("2. 在 Claude Code 中创建任务清单（TodoWrite）")
    print("3. 启动5个子智能体完成文章创作")
    print("\n准备好开始了吗？（按 Ctrl+C 取消）")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
