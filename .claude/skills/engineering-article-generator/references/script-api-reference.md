# 脚本 API 参考

> **艹，老王我给你准备了7个核心脚本的完整API参考！**
>
> **注意**：这是技术文档，开发者使用

---

## 目录

1. [common.py](#1-commonpy) - 公共工具模块
2. [orchestrate_searches.py](#2-orchestrate_searchespy) - 编排脚本（入口）
3. [web_searcher.py](#3-web_searcherpy) - 搜索模块
4. [deduplicator.py](#4-deduplicatorpy) - 去重模块
5. [article_fetcher.py](#5-article_fetcherpy) - 全文爬取模块
6. [data_validator.py](#6-data_validatorpy) - 数据验证模块（**最关键**）
7. [content_analyzer.py](#7-content_analyzerpy) - 内容分析模块
8. [article_generator.py](#8-article_generatorpy) - 文章生成模块

---

## 1. common.py

**职责**：提供公共工具函数和类

### 函数列表

#### 日志函数

```python
def setup_logger(name: str, log_file: Optional[Path] = None, level: int = logging.INFO) -> logging.Logger
```

**说明**：设置日志记录器

**参数**：
- `name`: 日志记录器名称
- `log_file`: 日志文件路径（可选）
- `level`: 日志级别（默认：INFO）

**返回**：配置好的日志记录器

**示例**：
```python
logger = setup_logger(__name__, Path("app.log"), logging.INFO)
logger.info("艹，日志记录成功")
```

---

#### 文件操作函数

```python
def read_json(file_path: Path) -> Optional[Dict[str, Any]]
```

**说明**：读取 JSON 文件

**参数**：
- `file_path`: JSON 文件路径

**返回**：JSON 数据（字典），如果失败返回 None

**示例**：
```python
data = read_json(Path("data.json"))
if data:
    print(data)
```

---

```python
def write_json(file_path: Path, data: Dict[str, Any], indent: int = 2) -> bool
```

**说明**：写入 JSON 文件

**参数**：
- `file_path`: JSON 文件路径
- `data`: 要写入的数据（字典）
- `indent`: 缩进空格数（默认：2）

**返回**：是否成功写入

**示例**：
```python
data = {"key": "value"}
success = write_json(Path("output.json"), data)
```

---

```python
def read_text(file_path: Path) -> Optional[str]
```

**说明**：读取文本文件

**参数**：
- `file_path`: 文本文件路径

**返回**：文件内容（字符串），如果失败返回 None

---

```python
def write_text(file_path: Path, content: str) -> bool
```

**说明**：写入文本文件

**参数**：
- `file_path`: 文本文件路径
- `content`: 要写入的内容

**返回**：是否成功写入

---

#### 时间戳函数

```python
def get_timestamp() -> str
```

**说明**：获取当前时间戳（ISO 8601 格式）

**返回**：时间戳字符串（例如：2026-01-22T12:30:15）

---

```python
def get_date(days_ago: int = 0) -> str
```

**说明**：获取日期（YYYY-MM-DD 格式）

**参数**：
- `days_ago`: 几天前（默认：0，即今天）

**返回**：日期字符串（例如：2026-01-22）

---

#### URL 处理函数

```python
def normalize_url(url: str) -> str
```

**说明**：标准化 URL（用于去重）

**参数**：
- `url`: 原始 URL

**返回**：标准化后的 URL

---

```python
def extract_domain(url: str) -> str
```

**说明**：提取域名

**参数**：
- `url`: URL

**返回**：域名（例如：www.example.com）

---

```python
def is_valid_url(url: str) -> bool
```

**说明**：验证 URL 格式是否有效

**参数**：
- `url`: URL

**返回**：是否有效

---

#### 数据验证函数

```python
def clean_text(text: str) -> str
```

**说明**：清理文本（移除多余的空白字符）

**参数**：
- `text`: 原始文本

**返回**：清理后的文本

---

#### 错误处理函数

```python
def handle_error(error: Exception, context: str = "") -> None
```

**说明**：统一的错误处理函数

**参数**：
- `error`: 异常对象
- `context`: 错误上下文（可选）

---

## 2. orchestrate_searches.py

**职责**：编排脚本（入口）

### 主函数

```python
def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="工程制造业文章创作器 - 编排脚本")

    # 必需参数
    parser.add_argument("--topic", type=str, required=True, help="文章主题")
    parser.add_argument("--article-type", type=str, required=True,
                       choices=["industry_analysis", "tech_research", "case_study", "feasibility_study"],
                       help="文章类型")
    parser.add_argument("--output", type=Path, required=True, help="输出目录")

    # 可选参数
    parser.add_argument("--company", type=str, help="主体公司名称")
    parser.add_argument("--industry", type=str, help="行业名称")
    parser.add_argument("--dimensions", type=str, help="搜索维度（逗号分隔）")

    args = parser.parse_args()

    # 参数验证
    # ...

    # 生成搜索任务配置
    search_task = generate_search_task(args)

    # 生成调用说明
    generate_instruction(args, search_task)
```

### 使用示例

```bash
python scripts/orchestrate_searches.py \
  --topic "工程机械智能化" \
  --article-type industry_analysis \
  --company "三一重工" \
  --industry "工程机械" \
  --dimensions "company,industry,china,global,media,influencer" \
  --output "E:\文章输出"
```

---

## 3. web_searcher.py

**职责**：执行7个维度的搜索

### 主要函数

```python
def search_dimensions(topic: str, company: str, industry: str,
                      dimensions: List[str], output_dir: Path) -> Dict[str, Any]:
    """
    执行多维度搜索

    Args:
        topic: 文章主题
        company: 主体公司名称
        industry: 行业名称
        dimensions: 搜索维度列表
        output_dir: 输出目录

    Returns:
        搜索结果字典
    """
```

### 搜索维度

| 维度 | 说明 | 查询示例 |
|------|------|----------|
| `company` | 公司官网和新闻 | `"{company}" 智能化 转型` |
| `industry` | 行业媒体和报告 | `"{industry}" 智能化 市场 规模` |
| `china` | 全国范围搜索 | `"{topic}" 中国 2024 2025` |
| `global` | 全球范围搜索 | `"{topic}" global 2024 2025` |
| `media` | 专业媒体报道 | `"{topic}" 报告 研究` |
| `influencer` | 行业从业者观点 | `"{topic}" 专家 观点` |
| `policy` | 政策文件和法规 | `"{topic}" 政策 支持 监管` |

---

## 4. deduplicator.py

**职责**：汇总搜索结果并去重

### 主要函数

```python
def deduplicate_search_results(search_results: Dict[str, Any],
                               min_articles: int = 10) -> Dict[str, Any]:
    """
    去重并排序搜索结果

    Args:
        search_results: 原始搜索结果
        min_articles: 最少保留的文章数量（默认：10）

    Returns:
        去重后的搜索结果
    """
```

### 质量评分

```python
def calculate_quality_score(article: Dict[str, Any]) -> float:
    """
    计算文章质量评分（0-10分）

    评分标准：
    1. 来源权威性（0-4分）
    2. 内容完整性（0-3分）
    3. 数据支撑（0-2分）
    4. 时效性（0-1分）

    Args:
        article: 文章数据字典

    Returns:
        质量评分（0-10分）
    """
```

---

## 5. article_fetcher.py

**职责**：爬取文章全文内容

### 主要函数

```python
def fetch_articles(deduped_results: Dict[str, Any],
                  output_dir: Path,
                  max_workers: int = 5) -> Dict[str, Any]:
    """
    批量爬取文章全文

    Args:
        deduped_results: 去重后的搜索结果
        output_dir: 输出目录
        max_workers: 最大并发数（默认：5）

    Returns:
        爬取结果字典
    """
```

### 爬取方法

```python
def fetch_article(url: str) -> Optional[Dict[str, Any]]:
    """
    爬取单篇文章

    Args:
        url: 文章 URL

    Returns:
        文章数据字典（包含标题、内容、作者、发布日期等）
    """
```

---

## 6. data_validator.py

**职责**：数据验证模块（**最关键**）

### 主要函数

#### URL验证

```python
def validate_urls(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    批量验证URL可访问性

    Args:
        articles: 文章列表

    Returns:
        验证结果字典
    """
```

```python
def validate_url(url: str) -> Dict[str, Any]:
    """
    验证单个URL可访问性

    Args:
        url: URL

    Returns:
        验证结果字典
    """
```

#### 可信度评分

```python
def calculate_credibility_scores(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    批量计算可信度评分

    Args:
        articles: 文章列表

    Returns:
        带可信度评分的文章列表
    """
```

```python
def calculate_credibility_score(article: Dict[str, Any]) -> float:
    """
    计算单篇文章的可信度评分（0-10分）

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
```

#### 数据点提取

```python
def extract_data_points(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    批量提取数据点

    Args:
        articles: 文章列表

    Returns:
        数据点列表
    """
```

```python
def extract_data_points_from_article(article: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    从单篇文章中提取数据点

    Args:
        article: 文章数据字典

    Returns:
        数据点列表
    """
```

#### 数据来源清单

```python
def generate_data_sources_summary(data_points: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    生成数据来源汇总清单

    Args:
        data_points: 数据点列表

    Returns:
        数据来源汇总清单
    """
```

### 数据点格式

```json
{
  "data": "效率提升18%",
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

---

## 7. content_analyzer.py

**职责**：分析已验证的搜索结果

### 主要函数

```python
def analyze_content(validated_results: Dict[str, Any],
                   article_type: str) -> Dict[str, Any]:
    """
    分析已验证的搜索结果

    Args:
        validated_results: 已验证的搜索结果
        article_type: 文章类型

    Returns:
        分析报告字典
    """
```

### 分析维度

```python
def extract_market_trends(data_points: List[Dict[str, Any]]) -> Dict[str, Any]:
    """提取市场趋势"""
```

```python
def extract_commercial_value(data_points: List[Dict[str, Any]]) -> Dict[str, Any]:
    """提取商业价值"""
```

```python
def extract_tech_innovation(data_points: List[Dict[str, Any]]) -> Dict[str, Any]:
    """提取技术创新"""
```

```python
def extract_policy_environment(data_points: List[Dict[str, Any]]) -> Dict[str, Any]:
    """提取政策环境"""
```

```python
def extract_cases(data_points: List[Dict[str, Any]]) -> Dict[str, Any]:
    """提取案例"""
```

---

## 8. article_generator.py

**职责**：生成Markdown文章

### 主要类

```python
class ArticleGenerator:
    """文章生成器类"""

    def __init__(self, analysis_report_path: Path, output_dir: Path):
        """
        初始化文章生成器

        Args:
            analysis_report_path: 内容分析报告路径（JSON）
            output_dir: 输出目录
        """
```

### 主要方法

```python
def generate(self, article_type: str) -> Path:
    """
    生成文章

    Args:
        article_type: 文章类型（industry_analysis、tech_research、case_study、feasibility_study）

    Returns:
        生成的文章文件路径
    """
```

### 文章生成方法

```python
def _generate_industry_analysis(self) -> str:
    """生成行业分析报告"""
```

```python
def _generate_tech_research(self) -> str:
    """生成技术研究文章"""
```

```python
def _generate_case_study(self) -> str:
    """生成案例研究/应用"""
```

```python
def _generate_feasibility_study(self) -> str:
    """生成可行性研究报告"""
```

---

## 总结

艹，老王我再总结一下这7个核心脚本的作用：

| 脚本 | 职责 | 输入 | 输出 |
|------|------|------|------|
| `common.py` | 公共工具函数 | - | 工具函数 |
| `orchestrate_searches.py` | 编排脚本（入口） | 命令行参数 | search_task.json<br>claude_instruction.md |
| `web_searcher.py` | 搜索模块 | search_task.json | search_results.json |
| `deduplicator.py` | 去重模块 | search_results.json | deduped_results.json |
| `article_fetcher.py` | 全文爬取模块 | deduped_results.json | fetched_articles.json |
| `data_validator.py` | 数据验证模块（**最关键**） | fetched_articles.json | validated_results.json |
| `content_analyzer.py` | 内容分析模块 | validated_results.json | analysis_report.json |
| `article_generator.py` | 文章生成模块 | analysis_report.json | {文章标题}.md |

**调用顺序**：
```
orchestrate_searches.py
→ web_searcher.py
→ deduplicator.py
→ article_fetcher.py
→ data_validator.py（最关键）
→ content_analyzer.py
→ article_generator.py
```

---

**End of script-api-reference.md**
