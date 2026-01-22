# 数据验证规则

> **艹，老王我提醒你一下：这是整个系统最重要的参考文档！**
>
> **核心目标**：确保数据真实有效，所有来源可追溯

---

## URL验证规则

### 验证流程

1. 发送HEAD请求（避免下载完整内容）
2. 允许重定向（最多3次）
3. 超时设置（10秒）
4. 返回状态码检查

### 验证标准

- ✅ 状态码 = 200：验证通过
- ❌ 状态码 != 200：验证失败（排除在分析之外）
- ⚠️ 超时或网络错误：重试3次（仍失败则排除）

### 质量控制

- 验证率必须 >= 95%（已验证URL / 总URL）
- 如果验证率 < 95%，自动扩展搜索范围（增加搜索维度或增加每个维度的文章数量）

### 实现代码示例

```python
def validate_url(url: str) -> Dict[str, Any]:
    """
    验证URL可访问性

    Args:
        url: URL

    Returns:
        验证结果字典
    """
    import requests
    from urllib.parse import urlparse

    result = {
        'url': url,
        'accessible': False,
        'status_code': None,
        'final_url': None,
        'error': None,
    }

    try:
        # 发送HEAD请求（避免下载完整内容）
        response = requests.head(
            url,
            allow_redirects=True,  # 允许重定向
            timeout=10  # 超时设置
        )

        # 检查状态码
        result['status_code'] = response.status_code
        result['final_url'] = response.url
        result['accessible'] = (response.status_code == 200)

    except requests.exceptions.Timeout:
        result['error'] = 'Timeout'
    except requests.exceptions.RequestException as e:
        result['error'] = str(e)
    except Exception as e:
        result['error'] = f'Unexpected error: {str(e)}'

    return result
```

---

## 可信度评分标准

### 评分维度（0-10分）

#### 1. 来源权威性（0-4分）

**权威机构（行业协会、政府机构）：4.0分**

- 中国工程机械工业协会（ccma.org.cn）
- 工信部（miit.gov.cn）
- 发改委（ndrc.gov.cn）
- 中国政府网（gov.cn）
- 各地政府网站（如：beijing.gov.cn、shanghai.gov.cn）

**专业媒体：3.0分**

- 第一工程机械（d1cm.com）
- 工程机械在线（cm.365sme.com）
- 艾瑞咨询（iresearch.com.cn）
- 易观分析（analysys.cn）
- 财新网（caixin.com）
- 财经网（finance.sina.com.cn）

**公司官网：2.0分**

- 三一重工（sanyglobal.com）
- 中联重科（zoomlion.com）
- 徐工集团（xcmg.com）
- 其他公司官网

**其他来源：1.0分**

- 个人博客
- 论坛帖子
- 社交媒体
- 未经验证的网站

#### 2. 内容完整性（0-3分）

- 文章长度 > 1000字：3.0分
- 文章长度 > 500字：2.0分
- 文章长度 <= 500字：1.0分

**计算方式**：
```python
content_length = len(article.get('content', ''))
if content_length > 1000:
    score = 3.0
elif content_length > 500:
    score = 2.0
else:
    score = 1.0
```

#### 3. 数据支撑（0-2分）

- 包含具体数据或案例：2.0分
- 缺少数据支撑：0分

**判断标准**：
```python
def has_data_support(content: str) -> bool:
    """
    判断文章是否包含数据支撑

    Args:
        content: 文章内容

    Returns:
        是否包含数据支撑
    """
    # 检查是否包含数字
    import re
    has_numbers = bool(re.search(r'\d+', content))

    # 检查是否包含百分比
    has_percentage = '%' in content

    # 检查是否包含关键词（如：万元、亿元、%等）
    keywords = ['万元', '亿元', '万亿', '%', '增长', '下降', '提升', '降低']
    has_keywords = any(keyword in content for keyword in keywords)

    return has_numbers or has_percentage or has_keywords
```

#### 4. 时效性（0-1分）

- 最近6个月：1.0分
- 6-12个月：0.8分
- 12-24个月：0.5分

**计算方式**：
```python
from datetime import datetime, timezone

def calculate_timeliness_score(publish_date: str) -> float:
    """
    计算时效性评分

    Args:
        publish_date: 发布日期（ISO 8601格式）

    Returns:
        时效性评分（0-1分）
    """
    try:
        # 解析发布日期
        pub_datetime = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))

        # 计算距离现在的天数
        now = datetime.now(timezone.utc)
        days_ago = (now - pub_datetime).days

        # 计算评分
        if days_ago <= 180:  # 最近6个月
            return 1.0
        elif days_ago <= 365:  # 6-12个月
            return 0.8
        elif days_ago <= 730:  # 12-24个月
            return 0.5
        else:  # 超过24个月
            return 0.0
    except:
        return 0.0
```

### 可信度分级

- **极高**（9.0-10.0分）：行业协会、政府机构
- **高**（7.0-8.9分）：专业媒体、研究机构
- **中**（5.0-6.9分）：公司官网、行业论坛
- **低**（<5.0分）：其他来源（需要人工审核）

### 完整计算示例

```python
def calculate_credibility_score(article: Dict[str, Any]) -> float:
    """
    计算文章来源的可信度评分（0-10分）

    Args:
        article: 文章数据字典

    Returns:
        可信度评分（0-10分）
    """
    score = 0.0

    # 1. 来源权威性（0-4分）
    domain = extract_domain(article.get('url', ''))
    authority_score = get_authority_score(domain)
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
    if has_data_support(article.get('content', '')):
        score += 2.0

    # 4. 时效性（0-1分）
    publish_date = article.get('publish_date', '')
    if publish_date:
        score += calculate_timeliness_score(publish_date)

    return min(score, 10.0)  # 最高10分
```

---

## 数据点提取规则

### 提取流程

1. 使用AI提取数据（数值、单位、上下文）
2. 验证数据真实性（必须明确出现在文章中）
3. 记录数据上下文（避免误读）
4. 标注完整来源（URL + 标题 + 域名 + 访问时间）

### 提取规则

- ✅ 只提取明确出现在文章中的数据（不允许AI幻觉）
- ✅ 必须提供数据上下文（例如："效率提升18%，在智能制造项目中应用后的效果"）
- ✅ 必须标注完整来源（URL + 标题 + 域名 + 访问时间）
- ✅ 必须验证数据真实性（人工审核关键数据点）

### 数据点格式

```json
{
  "data": "效率提升18%",
  "value": "18%",
  "context": "在智能制造项目中应用智能化技术后的效果",
  "category": "技术效果",
  "source_url": "https://www.sanyglobal.com/zh/news/20250315",
  "source_title": "三一重工智能化转型实践",
  "source_domain": "www.sanyglobal.com",
  "source_type": "company",
  "verified": true,
  "credibility_score": 8.5,
  "extracted_at": "2026-01-22T12:30:15",
  "access_time": "2026-01-22T12:30:15"
}
```

### 关键数据点（必须人工审核）

- **财务数据**（营业收入、利润、ROI）
- **市场数据**（市场规模、增长率、市场份额）
- **技术数据**（效率提升、成本降低、性能指标）
- **政策数据**（政策支持、补贴金额、税收优惠）

### 提取示例

**原始文章**：
```
三一重工在智能制造项目中应用了智能化技术，使得生产效率提升了18%，成本降低了15%。
项目总投资5000万元，预计投资回报期为2年。
```

**提取的数据点**：
```json
[
  {
    "data": "效率提升18%",
    "value": "18%",
    "context": "三一重工在智能制造项目中应用智能化技术后的效果",
    "category": "技术效果",
    "source_url": "https://www.sanyglobal.com/zh/news/20250315",
    "source_title": "三一重工智能化转型实践",
    "verified": true,
    "credibility_score": 8.5
  },
  {
    "data": "成本降低15%",
    "value": "15%",
    "context": "三一重工在智能制造项目中应用智能化技术后的效果",
    "category": "技术效果",
    "source_url": "https://www.sanyglobal.com/zh/news/20250315",
    "source_title": "三一重工智能化转型实践",
    "verified": true,
    "credibility_score": 8.5
  },
  {
    "data": "项目总投资5000万元",
    "value": "5000万元",
    "context": "三一重工智能制造项目的投资规模",
    "category": "财务数据",
    "source_url": "https://www.sanyglobal.com/zh/news/20250315",
    "source_title": "三一重工智能化转型实践",
    "verified": true,
    "credibility_score": 8.5
  },
  {
    "data": "预计投资回报期为2年",
    "value": "2年",
    "context": "三一重工智能制造项目的投资回报期",
    "category": "财务数据",
    "source_url": "https://www.sanyglobal.com/zh/news/20250315",
    "source_title": "三一重工智能化转型实践",
    "verified": true,
    "credibility_score": 8.5
  }
]
```

---

## 来源追溯格式

### 文章中的数据引用

```markdown
## 一、市场现状

### 1.1 市场规模

2025年，中国工程机械智能化市场规模达到**450亿元**，同比增长**18%**[^1]。主要驱动因素包括：
- 人工成本持续上升
- 安全监管要求提高
- 数字化转型需求增强

根据中国工程机械工业协会的数据，预计未来5年，工程机械智能化市场将保持**15-20%**的年均增长率[^2]。

[^1]: 数据来源：中国工程机械工业协会，《2025年工程机械智能化市场报告》，https://www.ccma.org.cn/report/2025-intelligent-machinery，访问时间：2026-01-22T10:30:15
[^2]: 数据来源：中国工程机械工业协会，《工程机械智能化发展趋势预测》，https://www.ccma.org.cn/report/2025-intelligent-machinery-trend，访问时间：2026-01-22T10:35:20
```

### 文章末尾的数据来源清单

```markdown
## 附录：完整数据来源清单

### 市场规模和增长数据

| 数据点 | 数值 | 来源 | URL | 访问时间 |
|--------|------|------|-----|----------|
| 2025年市场规模 | 450亿元 | 中国工程机械工业协会 | https://www.ccma.org.cn/report/2025-intelligent-machinery | 2026-01-22T10:30:15 |
| 同比增长率 | 18% | 中国工程机械工业协会 | https://www.ccma.org.cn/report/2025-intelligent-machinery | 2026-01-22T10:30:15 |
| 年均增长率 | 15-20% | 中国工程机械工业协会 | https://www.ccma.org.cn/report/2025-intelligent-machinery-trend | 2026-01-22T10:35:20 |

### 脚注

[^1]: 数据来源：中国工程机械工业协会，《2025年工程机械智能化市场报告》，https://www.ccma.org.cn/report/2025-intelligent-machinery，访问时间：2026-01-22T10:30:15
[^2]: 数据来源：中国工程机械工业协会，《工程机械智能化发展趋势预测》，https://www.ccma.org.cn/report/2025-intelligent-machinery-trend，访问时间：2026-01-22T10:35:20

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

---

## 质量控制标准

### 验收标准

- ✅ URL验证率必须 >= 95%（已验证URL / 总URL）
- ✅ 所有数据点必须标注完整来源（URL + 访问时间）
- ✅ 所有数据点必须包含访问时间戳
- ✅ 文章中每个数据点必须标注脚注[^1][^2]...
- ✅ 文章末尾生成"附录：完整数据来源清单"
- ✅ 数据来源清单包含：数据点、数值、来源、URL、访问时间
- ✅ 文章包含数据质量说明（总数据点、已验证比例、来源分布、可信度评分）
- ✅ 关键数据点必须人工审核（财务数据、市场数据）

### 失败处理

#### 1. URL验证率 < 95%

**解决方案**：自动扩展搜索范围
- 增加搜索维度（如：添加 policy、media 维度）
- 增加每个维度的文章数量（如：从10篇增加到20篇）

**代码示例**：
```python
def verify_url_validation_rate(search_results: List[Dict]) -> bool:
    """
    验证URL验证率是否达标

    Args:
        search_results: 搜索结果列表

    Returns:
        是否达标
    """
    total = len(search_results)
    verified = sum(1 for result in search_results if result.get('verified', False))

    if total == 0:
        return False

    validation_rate = (verified / total) * 100

    if validation_rate < 95.0:
        logger.warning(f"艹，URL验证率低于95%：{validation_rate:.1f}%")
        logger.info("正在自动扩展搜索范围...")
        # 自动扩展搜索范围
        expand_search_scope()
        return False

    return True
```

#### 2. 数据点提取失败

**解决方案**：记录错误并跳过该数据点（不影响整体流程）

**代码示例**：
```python
def extract_data_points_safely(article: Dict) -> List[Dict]:
    """
    安全地提取数据点

    Args:
        article: 文章数据

    Returns:
        数据点列表
    """
    data_points = []

    try:
        # 尝试提取数据点
        data_points = extract_data_points(article)
    except Exception as e:
        logger.error(f"艹，数据点提取失败：{article.get('url', '')}，错误：{e}")
        # 记录错误但不影响整体流程
        data_points = []

    return data_points
```

#### 3. 关键数据点不准确

**解决方案**：人工审核并修正（特别是财务数据、市场数据）

**代码示例**：
```python
def identify_key_data_points(data_points: List[Dict]) -> List[Dict]:
    """
    识别关键数据点（需要人工审核）

    Args:
        data_points: 所有数据点

    Returns:
        关键数据点列表
    """
    key_data_points = []

    for dp in data_points:
        category = dp.get('category', '')

        # 识别关键类别
        if category in ['财务数据', '市场数据', '技术数据', '政策数据']:
            dp['requires_manual_review'] = True
            key_data_points.append(dp)

    return key_data_points
```

---

## 常见问题

### Q1: 如何判断一个来源是否权威？

**A**: 根据域名和机构类型判断：
- 政府机构（gov.cn）：权威
- 行业协会（org.cn）：权威
- 专业媒体：权威
- 公司官网：中等
- 其他来源：低

### Q2: 如何避免AI幻觉？

**A**:
1. 只提取明确出现在文章中的数据
2. 必须提供数据上下文
3. 人工审核关键数据点
4. 验证数据真实性（与原文对照）

### Q3: 如何确保数据可追溯？

**A**:
1. 每个数据点标注完整来源（URL + 访问时间）
2. 文章中使用脚注[^1][^2]...
3. 文章末尾生成完整数据来源清单
4. 包含数据质量说明

### Q4: URL验证失败怎么办？

**A**:
1. 重试3次（仍失败则排除）
2. 记录错误日志
3. 如果验证率 < 95%，自动扩展搜索范围

---

## 总结

艹，老王我再强调一遍，数据验证是整个系统最关键的部分！

**核心原则**：
1. **URL验证**：确保所有来源可访问
2. **可信度评分**：确保来源权威性
3. **数据点提取**：只提取明确出现在文章中的数据
4. **来源追溯**：完整的脚注 + 数据来源清单
5. **质量控制**：验证率 >= 95%，关键数据点人工审核

**质量控制标准**：
- ✅ URL验证率必须 >= 95%
- ✅ 所有数据点必须标注完整来源
- ✅ 文章中每个数据点必须标注脚注
- ✅ 文章末尾生成完整数据来源清单
- ✅ 关键数据点必须人工审核

---

**End of data-validation-rules.md**
