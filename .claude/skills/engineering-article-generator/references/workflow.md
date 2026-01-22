# 工作流程指南

> **艹，老王我提醒你一下：按照这个流程操作，别tm乱搞！**
>
> **核心目标**：保证数据真实有效，输出高质量内容

---

## 完整工作流程（Step-by-Step）

### Step 1: 运行编排脚本

**命令示例**：

```bash
python scripts/orchestrate_searches.py \
  --topic "工程机械智能化" \
  --article-type industry_analysis \
  --company "三一重工" \
  --industry "工程机械" \
  --dimensions "company,industry,china,global,media,influencer" \
  --output "E:\文章输出"
```

**参数说明**：

| 参数 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| `--topic` | str | ✅ | 文章主题 | `"工程机械智能化"` |
| `--article-type` | str | ✅ | 文章类型 | `industry_analysis`、`tech_research`、`case_study`、`feasibility_study` |
| `--company` | str | ❌ | 主体公司名称 | `"三一重工"` |
| `--industry` | str | ❌ | 行业名称 | `"工程机械"` |
| `--dimensions` | str | ❌ | 搜索维度（逗号分隔） | `"company,industry,china,global,media,influencer,policy"` |
| `--output` | str | ✅ | 输出目录 | `"E:\文章输出"` |

**输出文件**：

```
{output}/tmp/
├── search_task.json          # 搜索任务配置
└── claude_instruction.md     # Claude Code 调用说明
```

**下一步**：打开 `{output}/tmp/claude_instruction.md`，按照说明继续操作。

---

### Step 2: 创建任务清单

**使用 TodoWrite 创建任务清单**：

```python
from superpowers import TodoWrite

TodoWrite([
    {"content": "读取调用说明和参考文档", "status": "pending"},
    {"content": "启动搜索子智能体（7个维度）", "status": "pending"},
    {"content": "启动去重和全文爬取子智能体", "status": "pending"},
    {"content": "启动数据验证子智能体（关键）", "status": "pending"},
    {"content": "启动内容分析子智能体", "status": "pending"},
    {"content": "启动文章生成子智能体", "status": "pending"},
    {"content": "汇总结果并清理临时文件", "status": "pending"},
])
```

**任务说明**：

1. **读取调用说明和参考文档**：了解任务要求和参数配置
2. **启动搜索子智能体**（7个维度）：执行搜索并返回结果
3. **启动去重和全文爬取子智能体**：去重、爬取全文
4. **启动数据验证子智能体**（**最关键**）：验证URL、计算可信度评分、提取数据点
5. **启动内容分析子智能体**：分析已验证的搜索结果
6. **启动文章生成子智能体**：生成Markdown文章
7. **汇总结果并清理临时文件**：完成并清理

---

### Step 3: 启动子智能体

艹，老王我现在给你提供完整的子智能体提示模板，你tm直接复制使用就行！

#### 子智能体1：搜索执行者

**提示模板**：

```
你是搜索执行者子智能体。

## 任务

调用 scripts/web_searcher.py 执行7个维度的搜索。

## 输入参数

- topic: "工程机械智能化"
- company: "三一重工"
- industry: "工程机械"
- dimensions: ["company", "industry", "china", "global", "media", "influencer"]
- search_task_file: "{output}/tmp/search_task.json"

## 输出

- {output}/tmp/search_results.json - 搜索结果（带完整来源信息）

## 要求

1. 每个维度搜索10-15篇文章
2. 限制搜索时间范围（最近两年：2024-01-22 至 2026-01-22）
3. 每个搜索结果必须记录完整来源信息（URL、标题、摘要、发布日期、访问时间）
4. 返回搜索统计（每个维度的文章数量）

## 工作流程

1. 读取 search_task.json 文件
2. 调用 web_searcher.py 执行搜索
3. 保存搜索结果到 search_results.json
4. 返回搜索统计

## 报告格式

- 总搜索结果数量：XXX篇
- 各维度搜索结果：
  - company: XX篇
  - industry: XX篇
  - china: XX篇
  - global: XX篇
  - media: XX篇
  - influencer: XX篇
```

---

#### 子智能体2：去重和全文爬取

**提示模板**：

```
你是去重和全文爬取子智能体。

## 任务

汇总搜索结果、去重、爬取全文。

## 输入参数

- search_results_file: "{output}/tmp/search_results.json"

## 输出

- {output}/tmp/deduped_results.json - 去重后的搜索结果
- {output}/tmp/fetched_articles.json - 全文内容（带元数据）

## 要求

1. 汇总所有维度的搜索结果
2. 标准化URL（去除查询参数）
3. 去重（识别重复的URL）
4. 质量排序（按质量评分，确保至少保留 10-15 篇高质量文章）
5. 批量爬取全文（使用 article_fetcher.py）
6. 记录完整的元数据（标题、作者、发布日期、URL、爬取时间）

## 工作流程

1. 读取 search_results.json 文件
2. 调用 deduplicator.py 去重并排序
3. 调用 article_fetcher.py 爬取全文
4. 保存结果到 deduped_results.json 和 fetched_articles.json
5. 返回爬取统计

## 报告格式

- 原始搜索结果：XXX篇
- 去重后：XXX篇
- 高质量文章（评分 >= 5.0）：XXX篇
- 成功爬取全文：XXX篇
- 爬取失败：XXX篇
```

---

#### 子智能体3：数据验证者（**最关键**）

**提示模板**：

```
你是数据验证子智能体，这是整个系统最关键的模块！

## 任务

验证所有搜索结果的真实性和可访问性，提取数据点，生成数据来源清单。

## 输入参数

- fetched_articles_file: "{output}/tmp/fetched_articles.json"

## 输出

- {output}/tmp/validated_results.json - 已验证的搜索结果（带数据点）

## 验证流程（严格）

### Step 1: URL验证

- 发送HEAD请求（避免下载完整内容）
- 允许重定向（最多3次）
- 超时设置（10秒）
- 返回状态码检查

**验证规则**：
- ✅ 状态码 = 200：验证通过
- ❌ 状态码 != 200：验证失败（排除在分析之外）
- ⚠️ 超时或网络错误：重试3次（仍失败则排除）

**质量控制**：
- 验证率必须 >= 95%（已验证URL / 总URL）

### Step 2: 可信度评分

**评分维度**（0-10分）：
1. 来源权威性（0-4分）
2. 内容完整性（0-3分）
3. 数据支撑（0-2分）
4. 时效性（0-1分）

**可信度分级**：
- 极高（9.0-10.0分）：行业协会、政府机构
- 高（7.0-8.9分）：专业媒体、研究机构
- 中（5.0-6.9分）：公司官网、行业论坛
- 低（<5.0分）：其他来源（需要人工审核）

### Step 3: 数据点提取和验证

**提取规则**：
- ✅ 只提取明确出现在文章中的数据（不允许AI幻觉）
- ✅ 必须提供数据上下文（例如："效率提升18%，在智能制造项目中应用后的效果"）
- ✅ 必须标注完整来源（URL + 标题 + 域名 + 访问时间）
- ✅ 必须验证数据真实性（人工审核关键数据点）

**数据点格式**：
```json
{
  "data": "效率提升18%",
  "context": "在智能制造项目中应用智能化技术后的效果",
  "source_url": "https://www.sanyglobal.com/zh/news/20250315",
  "source_title": "三一重工智能化转型实践",
  "source_domain": "www.sanyglobal.com",
  "verified": true,
  "credibility_score": 8.5,
  "extracted_at": "2026-01-22T12:30:15"
}
```

### Step 4: 生成数据来源清单

**数据来源清单格式**：
- 总数据点数量
- 按来源类型分类（权威机构、专业媒体、公司官网、其他）
- 按可信度分类（极高、高、中、低）
- 计算验证率（已验证数据点 / 总数据点）

## 工作流程

1. 读取 fetched_articles.json 文件
2. 调用 data_validator.py 执行验证
3. 保存结果到 validated_results.json
4. 返回验证统计

## 报告格式

- 总URL数量：XXX个
- 已验证URL：XXX个（XX.X%）
- 未验证URL：XXX个（XX.X%）
- 提取数据点：XXX个
- 关键数据点（需人工审核）：XXX个
- 可信度评分分布：
  - 极高（9.0-10.0分）：XXX个
  - 高（7.0-8.9分）：XXX个
  - 中（5.0-6.9分）：XXX个
  - 低（<5.0分）：XXX个
```

---

#### 子智能体4：内容分析者

**提示模板**：

```
你是内容分析子智能体。

## 任务

分析已验证的搜索结果，提取关键信息，针对管理层优化。

## 输入参数

- validated_results_file: "{output}/tmp/validated_results.json"

## 输出

- {output}/tmp/analysis_report.json - 结构化的分析报告

## 分析重点（针对管理层）

1. **市场趋势**：市场规模、增长率、驱动因素、竞争格局
2. **商业价值**：ROI、成本效益、竞争优势、投资回报期
3. **技术创新**：技术突破、应用场景、效率提升、成本降低
4. **政策环境**：政策红利、监管要求、行业标准
5. **案例效果**：客户案例、实施效果、数据支撑、经验总结

## 要求

1. 只使用已验证的数据（verified=true）
2. 聚焦商业价值（避免技术细节）
3. 必须使用数据支撑论点（每个论点必须有数据来源）
4. 针对管理层受众优化（结论导向，提供可执行建议）

## 工作流程

1. 读取 validated_results.json 文件
2. 调用 content_analyzer.py 执行分析
3. 保存结果到 analysis_report.json
4. 返回分析统计

## 报告格式

- 提取关键信息：
  - 市场趋势：XXX条
  - 商业价值：XXX条
  - 技术创新：XXX条
  - 政策环境：XXX条
  - 案例效果：XXX条
- 数据支撑：XXX个数据点
```

---

#### 子智能体5：文章生成者

**提示模板**：

```
你是文章生成子智能体。

## 任务

根据文章类型生成 Markdown 文章，应用管理层语言风格，整合数据和引用。

## 输入参数

- analysis_report_file: "{output}/tmp/analysis_report.json"
- article_type: "industry_analysis"  # 或 tech_research、case_study、feasibility_study

## 输出

- {output}/{文章标题}.md - Markdown 文章（带完整来源追溯）

## 数据引用格式（严格规范）

### 文章中的数据引用

```markdown
2025年，中国工程机械智能化市场规模达到**450亿元**，同比增长**18%**[^1]。

[^1]: 数据来源：中国工程机械工业协会，《2025年工程机械智能化市场报告》，https://www.ccma.org.cn/report/2025-intelligent-machinery，访问时间：2026-01-22T10:30:15
```

### 文章末尾的数据来源清单

```markdown
## 附录：完整数据来源清单

### 市场规模和增长数据

| 数据点 | 数值 | 来源 | URL | 访问时间 |
|--------|------|------|-----|----------|
| 2025年市场规模 | 450亿元 | 中国工程机械工业协会 | https://www.ccma.org.cn/report/2025-intelligent-machinery | 2026-01-22T10:30:15 |
| 同比增长率 | 18% | 中国工程机械工业协会 | https://www.ccma.org.cn/report/2025-intelligent-machinery | 2026-01-22T10:30:15 |

### 数据质量说明

- 总数据点：**245个**
- 已验证来源：**238个**（97.1%）
- 权威来源（行业协会、政府机构）：**89个**（36.3%）
- 专业媒体来源：**112个**（45.7%）
- 公司官网来源：**37个**（15.1%）
- 其他来源：**7个**（2.9%）

**来源可信度评分**：
- 9.0-10.0分（极高）：**58个**
- 7.0-8.9分（高）：**124个**
- 5.0-6.9分（中）：**56个**
- 5.0分以下（低）：**7个**（已排除）
```

## 管理层语言风格

**应该做的**：
- 聚焦商业价值（ROI、成本效益、竞争优势）
- 使用数据和案例支撑论点
- 结论导向，提供可执行的建议
- 语言简洁明了，避免技术术语

**不应该做的**：
- 避免技术细节和代码示例
- 避免底层实现原理
- 避免过于学术化的表达
- 避免没有数据支撑的观点

## 工作流程

1. 读取 analysis_report.json 文件
2. 根据文章类型选择生成方法
3. 应用管理层语言风格
4. 整合数据和引用（带完整来源追溯）
5. 保存文章到 {output}/{文章标题}.md
6. 返回文章生成状态

## 报告格式

- 文章类型：XXX
- 文章标题：XXX
- 输出路径：XXX
- 数据点数量：XXX个
- 引用来源：XXX个
```

---

### Step 4: 汇总结果并清理临时文件

**职责**：
- 汇总所有子任务结果
- 删除 `{output}/tmp/` 临时文件（成功时）
- 保留临时文件（失败时，便于调试）
- 标记所有任务为 completed

**清理规则**：
- ✅ 成功后删除临时文件（节省磁盘空间）
- ✅ 失败时保留临时文件（便于调试）

---

## 临时文件结构

```
{output}/tmp/
├── search_task.json              # 搜索任务配置
├── claude_instruction.md         # Claude Code 调用说明
├── search_results.json           # 搜索结果（带完整来源信息）
├── deduped_results.json          # 去重后的搜索结果
├── fetched_articles.json         # 全文内容（带元数据）
├── validated_results.json        # 已验证的搜索结果（带数据点）
└── analysis_report.json          # 结构化的分析报告
```

**文件说明**：

| 文件 | 说明 | 生成阶段 |
|------|------|----------|
| `search_task.json` | 搜索任务配置 | Step 1 |
| `claude_instruction.md` | Claude Code 调用说明 | Step 1 |
| `search_results.json` | 搜索结果（带完整来源信息） | Step 3-1 |
| `deduped_results.json` | 去重后的搜索结果 | Step 3-2 |
| `fetched_articles.json` | 全文内容（带元数据） | Step 3-2 |
| `validated_results.json` | 已验证的搜索结果（带数据点） | Step 3-3 |
| `analysis_report.json` | 结构化的分析报告 | Step 3-4 |

---

## 清理规则

### 成功时

**自动删除临时文件**：
```python
import shutil
from pathlib import Path

def cleanup_temp_files(output_dir: Path) -> None:
    """
    清理临时文件

    Args:
        output_dir: 输出目录
    """
    tmp_dir = output_dir / "tmp"

    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
        print(f"艹，临时文件已清理：{tmp_dir}")
```

### 失败时

**保留临时文件**：
- 不删除临时文件
- 记录错误日志
- 便于调试和问题排查

---

## 常见问题

### Q1: 搜索结果太少怎么办？

**A**: 增加搜索维度或增加每个维度的文章数量

### Q2: URL验证率低于95%怎么办？

**A**: 自动扩展搜索范围（增加搜索维度或增加每个维度的文章数量）

### Q3: 数据点提取不准确怎么办？

**A**: 人工审核关键数据点（特别是财务数据、市场数据）

### Q4: 文章生成不符合管理层风格怎么办？

**A**: 在提示词中强调"聚焦商业价值"和"数据支撑论点"

---

## 总结

艹，老王我再强调一遍工作流程：

**4个主要步骤**：
1. **Step 1**: 运行编排脚本（准备数据）
2. **Step 2**: 创建任务清单（TodoWrite）
3. **Step 3**: 启动5个子智能体（按顺序执行）
4. **Step 4**: 汇总结果并清理临时文件

**关键质量控制点**：
- ✅ URL验证率必须 >= 95%
- ✅ 所有数据点必须标注完整来源
- ✅ 文章中每个数据点必须标注脚注
- ✅ 文章末尾生成完整数据来源清单
- ✅ 关键数据点必须人工审核

---

**End of workflow.md**
