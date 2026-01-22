---
name: engineering-article-generator
description: "输出一篇工程、重型机械相关的可行性研究报告"
---

# 工程制造业文章创作器

> **核心目标**：保证数据真实有效，输出高质量内容
>
> **文章类型**：行业分析报告、技术研究文章、案例研究/应用、可行性研究报告
>
> **数据验证**：URL验证 + 可信度评分 + 数据点提取 + 完整来源追溯

---

## 核心原则

1. **数据真实有效**（最关键）
   - 所有URL必须验证可访问性（返回200状态码）
   - 所有数据点必须标注完整来源（URL + 访问时间）
   - 验证率必须 >= 95%

2. **多维度搜索**（7个维度）
   - 公司、行业、全国、全球、媒体、从业者、政策

3. **严格数据验证**
   - URL验证（可访问性检查）
   - 可信度评分（权威机构、专业媒体、公司官网）
   - 数据点提取和验证（AI辅助 + 人工审核）

4. **管理层导向**
   - 聚焦商业价值、ROI、市场趋势
   - 结论导向，提供可执行的建议

5. **完整来源追溯**
   - 脚注 + 数据来源清单 + 质量说明

---

## 快速开始

### Step 1: 运行编排脚本（准备数据）

```bash
python scripts/orchestrate_searches.py \
  --topic "工程机械智能化" \
  --article-type industry_analysis \
  --company "三一重工" \
  --industry "工程机械" \
  --dimensions "company,industry,china,global,media,influencer" \
  --output "E:\文章输出"
```

**输出文件**：
- `{output}/tmp/search_task.json` - 搜索任务配置
- `{output}/tmp/claude_instruction.md` - Claude Code 调用说明

### Step 2: 创建任务清单并启动子智能体

创建任务清单（TodoWrite），然后按顺序启动5个子智能体：
1. 搜索执行者（7个维度）
2. 去重和全文爬取
3. 数据验证者（**最关键**）
4. 内容分析者
5. 文章生成者

详细工作流程见 `references/workflow.md`

---

## 参考文档

详细的参考文档位于 `references/` 目录：

- **workflow.md**（工作流程指南）- 完整的 Step-by-Step 工作流程
- **data-validation-rules.md**（数据验证规则）- **最重要的参考文档**
- **article-prompts.md**（文章类型模板）- 4种文章类型的提示词模板
- **script-api-reference.md**（脚本API参考）- 9个核心脚本的API参考
- **examples.md**（使用示例）- 4个完整的使用示例
- **tone-guide.md**（管理层语言风格指南）- 管理层语言风格指南

**使用建议**：SKILL.md 只提供快速参考，详细操作请查阅参考文档。

---

## 参数说明

### orchestrate_searches.py 参数详解

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `--topic` | str | ✅ | 文章主题 |
| `--article-type` | str | ✅ | 文章类型（industry_analysis、tech_research、case_study、feasibility_study） |
| `--company` | str | ❌ | 主体公司名称 |
| `--industry` | str | ❌ | 行业名称 |
| `--dimensions` | str | ❌ | 搜索维度（逗号分隔：company,industry,china,global,media,influencer,policy） |
| `--output` | str | ✅ | 输出目录 |

**详细说明**见 `references/workflow.md`

---

## 文章类型

| 类型 | 说明 | 目标受众 |
|------|------|----------|
| `industry_analysis` | 行业分析报告 | 管理层/决策者 |
| `tech_research` | 技术研究文章 | 技术管理层 |
| `case_study` | 案例研究/应用 | 管理层/决策者 |
| `feasibility_study` | 可行性研究报告 | 管理层/决策者 |

**详细说明**见 `references/article-prompts.md`

---

## 常见问题

### Q1: URL验证率低于95%怎么办？

**A**: 自动扩展搜索范围（增加搜索维度或增加每个维度的文章数量）

### Q2: 数据点提取不准确怎么办？

**A**: 人工审核关键数据点（特别是财务数据、市场数据）

### Q3: 文章生成不符合管理层风格怎么办？

**A**: 在提示词中强调"聚焦商业价值"和"数据支撑论点"，参考 `references/tone-guide.md`

### Q4: 如何确保数据真实性？

**A**:
1. URL验证（确保所有来源可访问）
2. 可信度评分（确保来源权威性）
3. 数据点提取（只提取明确出现在文章中的数据）
4. 人工审核关键数据点

**详细规则**见 `references/data-validation-rules.md`

---

## 质量控制标准

- ✅ URL验证率必须 >= 95%（已验证URL / 总URL）
- ✅ 所有数据点必须标注完整来源（URL + 访问时间）
- ✅ 文章中每个数据点必须标注脚注[^1][^2]...
- ✅ 文章末尾生成"附录：完整数据来源清单"
- ✅ 关键数据点必须人工审核（财务数据、市场数据）

**详细规则**见 `references/data-validation-rules.md`

---

## 技术栈

- **Python 3.8+**
- **requests** - HTTP请求库（用于爬取文章）
- **BeautifulSoup4** - HTML解析库（用于提取文章正文）
- **MCP工具** - web search + web reader（提高效率）

---

## 目录结构

```
.claude/skills/engineering-article-generator/
├── SKILL.md                                  # 本文件
├── requirements.txt                          # Python 依赖清单
├── scripts/                                  # 核心脚本
│   ├── __init__.py                          # 包初始化文件
│   ├── common.py                            # 公共工具模块
│   ├── orchestrate_searches.py              # 编排脚本（入口）
│   ├── web_searcher.py                      # 搜索模块
│   ├── deduplicator.py                      # 去重模块
│   ├── article_fetcher.py                   # 全文爬取模块
│   ├── data_validator.py                    # 数据验证模块（最关键）
│   ├── content_analyzer.py                  # 内容分析模块
│   └── article_generator.py                 # 文章生成模块
└── references/                               # 参考文档
    ├── workflow.md                          # 工作流程指南
    ├── data-validation-rules.md             # 数据验证规则（最关键）
    ├── article-prompts.md                   # 文章类型模板
    ├── script-api-reference.md              # 脚本API参考
    ├── examples.md                          # 使用示例
    └── tone-guide.md                        # 管理层语言风格指南
```
