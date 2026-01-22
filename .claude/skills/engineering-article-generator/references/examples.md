# 使用示例

> **艹，老王我给你准备了4个完整的使用示例，直接复制用就行！**
>
> **注意**：示例中的路径和参数需要根据实际情况修改

---

## 示例1：行业分析报告

### 需求

生成工程机械智能化行业分析报告

### 命令

```bash
python scripts/orchestrate_searches.py \
  --topic "工程机械智能化" \
  --article-type industry_analysis \
  --company "三一重工" \
  --industry "工程机械" \
  --dimensions "company,industry,china,global,media,influencer" \
  --output "E:\文章输出"
```

### 输出

- **文件名**：`工程机械智能化_行业分析报告_20260122.md`
- **数据质量**：
  - 总数据点：245个
  - 已验证来源：238个（97.1%）
  - 权威来源：89个（36.3%）
  - 专业媒体来源：112个（45.7%）

### 文章结构

```
一、市场现状
  1.1 市场规模
  1.2 增长趋势
  1.3 驱动因素

二、商业价值
  2.1 ROI 分析
  2.2 成本效益
  2.3 竞争优势

三、技术创新
  3.1 技术突破
  3.2 应用场景
  3.3 效果评估

四、政策环境
  4.1 政策支持
  4.2 监管要求

附录：完整数据来源清单
```

---

## 示例2：技术研究文章

### 需求

生成工程机械物联网技术研究文章

### 命令

```bash
python scripts/orchestrate_searches.py \
  --topic "工程机械物联网技术" \
  --article-type tech_research \
  --industry "工程机械" \
  --dimensions "industry,china,global,media" \
  --output "E:\文章输出"
```

### 输出

- **文件名**：`工程机械物联网技术_技术研究文章_20260122.md`
- **数据质量**：
  - 总数据点：189个
  - 已验证来源：183个（96.8%）
  - 技术文献：67个（35.4%）
  - 案例数据：45个（23.8%）

### 文章结构

```
一、技术背景
  1.1 物联网技术概述
  1.2 工程机械应用场景
  1.3 技术发展趋势

二、技术原理
  2.1 感知层技术
  2.2 网络层技术
  2.3 平台层技术
  2.4 应用层技术

三、技术突破
  3.1 低功耗广域网
  3.2 边缘计算
  3.3 人工智能集成

四、应用场景
  4.1 远程监控
  4.2 预测性维护
  4.3 智能调度

五、效果评估
  5.1 技术性能
  5.2 经济效益
  5.3 实施案例

附录：完整数据来源清单
```

---

## 示例3：案例研究/应用

### 需求

生成三一重工智能化转型案例研究

### 命令

```bash
python scripts/orchestrate_searches.py \
  --topic "三一重工智能化转型" \
  --article-type case_study \
  --company "三一重工" \
  --industry "工程机械" \
  --dimensions "company,media,influencer" \
  --output "E:\文章输出"
```

### 输出

- **文件名**：`三一重工智能化转型_案例研究_20260122.md`
- **数据质量**：
  - 总数据点：156个
  - 已验证来源：152个（97.4%）
  - 公司官方数据：89个（57.1%）
  - 媒体报道：67个（42.9%）

### 文章结构

```
一、案例背景
  1.1 公司概况
  1.2 转型动机
  1.3 转型目标

二、实施方案
  2.1 智能制造
  2.2 智能服务
  2.3 智能管理

三、实施效果
  3.1 运营效率提升
  3.2 成本降低
  3.3 质量提升
  3.4 客户满意度提高

四、经验总结
  4.1 成功因素
  4.2 挑战与应对
  4.3 复制推广建议

附录：完整数据来源清单
```

---

## 示例4：可行性研究报告

### 需求

生成太重集团工程机械智能化改造可行性研究报告

### 命令

```bash
python scripts/orchestrate_searches.py \
  --topic "太重集团工程机械智能化改造" \
  --article-type feasibility_study \
  --company "太重集团" \
  --industry "工程机械" \
  --dimensions "company,industry,china,global,media,policy,influencer" \
  --output "E:\文章输出"
```

### 输出

- **文件名**：`太重集团工程机械智能化改造_可行性研究报告_20260122.md`
- **数据质量**：
  - 总数据点：312个
  - 已验证来源：298个（95.5%）
  - 市场数据：98个（31.4%）
  - 技术数据：89个（28.5%）
  - 政策数据：67个（21.5%）

### 文章结构

```
一、项目背景
  1.1 主体公司（太重集团）
  1.2 项目背景
  1.3 项目目标

二、市场分析
  2.1 市场规模
  2.2 增长趋势
  2.3 竞争格局

三、技术可行性
  3.1 技术成熟度
  3.2 技术适配性
  3.3 实施难度

四、商业价值
  4.1 ROI 分析
  4.2 成本效益
  4.3 投资回报期

五、政策环境
  5.1 政策支持
  5.2 监管要求
  5.3 行业标准

六、全球同行对比
  6.1 三一重工
  6.2 中联重科
  6.3 徐工集团
  6.4 卡特彼勒（Caterpillar）

七、可行性结论
  7.1 可行性评分
  7.2 结论
  7.3 建议

附录：完整数据来源清单
```

---

## 参数说明

### article-type（文章类型）

| 值 | 说明 | 适用场景 |
|---|------|---------|
| `industry_analysis` | 行业分析报告 | 分析整个行业的市场趋势、商业价值、技术创新、政策环境 |
| `tech_research` | 技术研究文章 | 深入分析某项技术的原理、应用场景、效果评估 |
| `case_study` | 案例研究/应用 | 展示某家公司或某个项目的实际应用效果和经验总结 |
| `feasibility_study` | 可行性研究报告 | 评估某个项目的可行性，包括市场、技术、商业、政策等多个维度 |

### dimensions（搜索维度）

| 值 | 说明 | 适用场景 |
|---|------|---------|
| `company` | 公司官网和新闻 | 案例研究、可行性研究（需要主体公司详细信息） |
| `industry` | 行业媒体和报告 | 行业分析、技术研究（需要行业数据和趋势） |
| `china` | 全国范围搜索 | 需要国内市场数据和政策信息 |
| `global` | 全球范围搜索 | 需要国际市场趋势和同行对比 |
| `media` | 专业媒体报道 | 需要新闻报道和专家观点 |
| `influencer` | 行业从业者观点 | 需要行业专家和实践者观点 |
| `policy` | 政策文件和法规 | 可行性研究（需要政策环境和监管要求） |

### 推荐组合

**行业分析报告**：
```bash
--dimensions "company,industry,china,global,media,influencer"
```

**技术研究文章**：
```bash
--dimensions "industry,china,global,media"
```

**案例研究/应用**：
```bash
--dimensions "company,media,influencer"
```

**可行性研究报告**：
```bash
--dimensions "company,industry,china,global,media,policy,influencer"
```

---

## 完整工作流程示例

### Step 1: 运行编排脚本

```bash
python scripts/orchestrate_searches.py \
  --topic "工程机械智能化" \
  --article-type industry_analysis \
  --company "三一重工" \
  --industry "工程机械" \
  --dimensions "company,industry,china,global,media,influencer" \
  --output "E:\文章输出"
```

### Step 2: 创建任务清单

```python
from superpowers import TodoWrite

TodoWrite([
    {"content": "读取调用说明和参考文档", "status": "in_progress"},
    {"content": "启动搜索子智能体（7个维度）", "status": "pending"},
    {"content": "启动去重和全文爬取子智能体", "status": "pending"},
    {"content": "启动数据验证子智能体（关键）", "status": "pending"},
    {"content": "启动内容分析子智能体", "status": "pending"},
    {"content": "启动文章生成子智能体", "status": "pending"},
    {"content": "汇总结果并清理临时文件", "status": "pending"},
])
```

### Step 3: 启动子智能体

按照 `workflow.md` 中的提示模板，依次启动5个子智能体。

### Step 4: 汇总结果

成功后，临时文件自动清理，最终文章保存在：
```
E:\文章输出\工程机械智能化_行业分析报告_20260122.md
```

---

## 常见问题

### Q1: 如何修改搜索范围？

**A**: 调整 `--dimensions` 参数，添加或删除搜索维度

### Q2: 如何提高数据质量？

**A**:
1. 增加搜索维度（如：添加 policy、media）
2. 增加搜索时间范围（修改脚本中的时间参数）
3. 优化搜索查询（添加更具体的关键词）

### Q3: 如何生成多种文章类型？

**A**: 多次运行编排脚本，每次指定不同的 `--article-type`

### Q4: 如何自定义输出文件名？

**A**: 修改 `article_generator.py` 中的 `_generate_filename` 方法

---

## 总结

艹，老王我给你总结一下使用这个 skill 的要点：

**核心步骤**：
1. 运行编排脚本（准备数据）
2. 创建任务清单（TodoWrite）
3. 启动5个子智能体（按顺序执行）
4. 汇总结果并清理临时文件

**关键参数**：
- `--topic`：文章主题（必需）
- `--article-type`：文章类型（必需）
- `--dimensions`：搜索维度（可选，推荐根据文章类型选择）
- `--output`：输出目录（必需）

**质量控制**：
- URL验证率必须 >= 95%
- 所有数据点必须标注完整来源
- 文章中每个数据点必须标注脚注
- 文章末尾生成完整数据来源清单

---

**End of examples.md**
