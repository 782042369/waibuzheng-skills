# Weekly Report Generator

> 最后更新：2026-01-16 14:20:00

自动化生成专业周报文档，从 Git 提交记录转换为面向领导的工作汇报。

## ✨ 特性

- 📅 **灵活时间解析**：支持"本周"、"上周"、"2025.1.10-2025.1.15"等多种时间表达
- 🧠 **智能内容清洗**：将技术术语转换为业务语言
- 📊 **两种输出方式**：按天分类（周一到周五）或合并输出（凝练任务）
- 🔄 **多项目支持**：汇总多个项目的提交记录
- 🎨 **自定义风格**：基于用户提供的示例周报模仿生成
- 📝 **多格式输出**：支持 Markdown (.md) 和 Word (.docx)
- 🔍 **模板分析**：自动分析示例模板结构，精确模仿格式

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

**依赖清单**：
- `gitpython>=3.1.40` - Git 操作库
- `python-docx>=0.8.11` - Word 文件读写库（可选，仅 Word 输出需要）

### 基本使用

周报生成遵循 **5 步工作流程**：

#### Step 1: 收集信息

准备以下信息：
- **项目路径**：单个或多个项目路径
- **时间范围**：如"本周"、"上周"、"2025.1.10-2025.1.15"
- **示例周报**（可选）：提供示例让 AI 模仿风格
- **输出文件名**：如"20250115周报.md"

#### Step 2: 获取 Git 日志

```bash
python scripts/get_git_logs.py \
  --paths "/path/to/project" \
  --since "2025-01-13" \
  --until "2025-01-17"
```

**返回格式**（JSON）：
```json
{
  "start_date": "2025-01-13",
  "end_date": "2025-01-17",
  "total_commits": 15,
  "commits_by_day": {
    "周一": [...],
    "周二": [...],
    "周三": [],
    "周四": [...],
    "周五": [...]
  }
}
```

#### Step 3: 分析示例模板（可选）

如果有示例周报文件，先分析其结构：

```bash
# 分析 Markdown 模板
python scripts/analyze_template.py \
  --template "/path/to/template.md" \
  --output "template_structure.json"

# 分析 Word 模板
python scripts/analyze_template.py \
  --template "/path/to/template.docx"
```

#### Step 4: AI 清洗内容

基于 `references/report-prompts.md` 的规则清洗内容：
- 将技术术语转换为业务语言
- 合并同类工作，避免碎片化
- 按天分类或合并输出

#### Step 5: 导出周报

```bash
# Markdown 输出（推荐）
python scripts/export_report.py \
  --content "AI清洗后的完整周报内容" \
  --output "./output" \
  --filename "周报.md"

# Word 输出
python scripts/export_report.py \
  --content "AI清洗后的完整周报内容" \
  --output "./output" \
  --filename "周报.docx"

# 自动文件名（默认 Markdown）
python scripts/export_report.py \
  --content "AI清洗后的完整周报内容" \
  --output "./output" \
  --start-date "2025-01-13" \
  --end-date "2025-01-17"
# 生成：output/周报20250113-20250117.md
```

## 📖 详细文档

| 文档 | 说明 |
|------|------|
| [SKILL.md](./SKILL.md) | 核心功能文档，完整的工作流程和使用场景 |
| [CLAUDE.md](./CLAUDE.md) | 实现细节，API 文档和架构设计 |
| [references/report-prompts.md](./references/report-prompts.md) | AI 内容清洗规则和术语转换表 |

## 🎯 使用场景

### 场景1：基本周报生成

```bash
# 1. 获取本周的 Git 日志
python scripts/get_git_logs.py \
  --paths "/path/to/project" \
  --since "2025-01-13" \
  --until "2025-01-17"

# 2. AI 清洗内容（复制输出给 AI）

# 3. 导出周报
python scripts/export_report.py \
  --content "清洗后的内容" \
  --output "./output" \
  --filename "20250115周报.md"
```

### 场景2：多项目汇总

```bash
python scripts/get_git_logs.py \
  --paths "/path/proj1,/path/proj2,/path/proj3" \
  --since "2025-01-13" \
  --until "2025-01-17"
```

### 场景3：使用示例风格

```bash
# 1. 分析示例模板
python scripts/analyze_template.py \
  --template "/path/to/example.docx" \
  --output "template_structure.json"

# 2. 将模板结构复制给 AI，让 AI 基于模板生成周报

# 3. 导出周报
python scripts/export_report.py \
  --content "AI基于模板生成的内容" \
  --output "./output" \
  --filename "周报.docx"
```

## 📂 项目结构

```
weekly-report-generator/
├── SKILL.md                 # 核心功能文档（必需）
├── CLAUDE.md                # AI 上下文和实现细节
├── README.md                # 本文件
├── requirements.txt         # Python 依赖
├── scripts/                 # 核心脚本
│   ├── get_git_logs.py      # Git 日志获取
│   ├── export_report.py     # 周报导出
│   └── analyze_template.py  # 模板分析
└── references/              # 参考文档
    └── report-prompts.md    # 内容清洗规则
```

## 🛠️ 核心脚本说明

### get_git_logs.py

**功能**：获取 Git 日志并按工作日分组

**参数**：
- `--paths`（必需）：项目路径列表，用逗号分隔
- `--since`（必需）：开始日期（YYYY-MM-DD 格式）
- `--until`（必需）：结束日期（YYYY-MM-DD 格式）

**特性**：
- ✅ 只返回工作日（周一到周五）的提交
- ✅ 支持多项目聚合
- ✅ 按天分组
- ✅ 输入验证：日期格式、路径有效性检查

### analyze_template.py

**功能**：分析周报模板文件（Markdown 或 Word），提取结构化信息

**参数**：
- `--template`（必需）：模板文件路径（支持 .md、.docx）
- `--output`（可选）：输出 JSON 文件路径

**返回数据**（JSON）：
```json
{
  "type": "markdown",
  "structure": {
    "title": "模板标题",
    "sections": [...]
  },
  "variables": {
    "{{变量名}}": {...}
  },
  "raw_content": "完整模板内容"
}
```

**支持的功能**：
- ✅ 自动检测文件类型（.md / .docx）
- ✅ 提取标题层级结构
- ✅ 识别变量占位符
- ✅ 返回完整的原始内容

### export_report.py

**功能**：将 AI 生成的周报内容写入文件

**参数**：
- `--content`（必需）：完整的周报内容（Markdown 格式）
- `--output`（必需）：输出目录路径
- `--filename`（可选）：输出文件名
- `--start-date`（可选）：开始日期（用于自动文件名）
- `--end-date`（可选）：结束日期（用于自动文件名）

**自动格式检测**：
- `.md` → Markdown 格式
- `.docx` → Word 格式
- 无扩展名 → 默认 Markdown 格式

**自动文件名生成**：
- 格式：`周报YYYYMMDD-YYYYMMDD.md`
- 示例：`周报20250113-20250117.md`

## 🧪 测试方法

### 手动测试

```bash
# 1. 测试单个项目
python scripts/get_git_logs.py \
  --paths "/path/to/test-project" \
  --since "2025-01-13" \
  --until "2025-01-17"

# 2. 测试多项目聚合
python scripts/get_git_logs.py \
  --paths "/path/proj1,/path/proj2,/path/proj3" \
  --since "2025-01-13" \
  --until "2025-01-17"

# 3. 测试模板分析
python scripts/analyze_template.py \
  --template "/path/to/template.md"

# 4. 测试周报导出
python scripts/export_report.py \
  --content "# 测试周报\n\n1. 完成功能A\n2. 优化功能B" \
  --output "./output" \
  --filename "test.md"
```

## 🤝 贡献指南

欢迎贡献！请遵循以下规范：

1. **代码风格**：遵循 PEP 8
2. **注释**：使用中文注释
3. **文档**：更新相关文档
4. **测试**：确保代码质量

## 📝 常见问题

### Q1: 周末的提交会被过滤吗？

**A**: 是的，脚本只会保留周一到周五的提交。

### Q2: 如何处理多项目汇总？

**A**: 使用逗号分隔多个项目路径：
```bash
--paths "/path/proj1,/path/proj2,/path/proj3"
```

### Q3: 如何自定义周报模板？

**A**: 有两种方式：
1. 提供示例周报文本，AI 会模仿风格
2. 提供示例周报文件（.md 或 .docx），调用 `analyze_template.py` 分析

### Q4: Word 输出需要什么依赖？

**A**: 需要安装 `python-docx`：
```bash
pip install python-docx
```

### Q5: 如何确保周报内容符合要求？

**A**:
1. 提供示例周报，AI 会严格模仿
2. AI 会自动转换技术术语为业务语言
3. AI 会合并同类工作，避免碎片化
4. 生成后可以手动微调

## 📄 许可证

MIT License

## 🙏 致谢

本 Skill 基于 [skill-creator](https://github.com/anthropics/skills) 最佳实践开发。

---

**回到 [项目根目录](../../README.md) | [查看核心文档](./SKILL.md) | [查看实现细节](./CLAUDE.md)**
