# 周报生成器使用示例

本文档提供常见使用场景的完整示例，帮助你快速上手周报生成器。

---

## 示例1：生成本月周报（Markdown格式）

### 场景
生成本月所有周的周报，使用简单的Markdown格式，不需要Word模板。

### 命令

```bash
python scripts/orchestrate_reports.py \
  --paths "E:\A项目项目" \
  --time "本月" \
  --output "E:\周报\2025年1月"
```

### 输出

```
E:\周报\2025年1月\
├── tmp\                              # 临时文件（自动清理）
│   ├── time_result.json
│   ├── week_01-task.json
│   ├── week_01-log.json
│   ├── week_01-report.json
│   ├── week_02-task.json
│   └── ...
├── 第1周周报.md                      # 最终周报
├── 第2周周报.md
├── 第3周周报.md
├── 第4周周报.md
└── 第5周周报.md（如果本月有5周）
```

### 说明

- `--time "本月"`：自动解析本月1日到最后一日，并按自然周（周一到周日）划分
- 不提供 `--template` 参数：使用默认的Markdown格式
- 不提供 `--format` 参数：默认使用 `md` 格式

---

## 示例2：使用Word模板

### 场景
使用公司提供的Word模板生成周报，确保格式符合领导要求。

### 准备工作

1. 准备Word模板文件（例如 `E:\周报模板.docx`）
2. 在模板中定义变量，例如：
   - `{{title}}` - 周报标题
   - `{{date}}` - 时间范围
   - `{{content}}` - 工作内容
   - `{{future_plan}}` - 下周计划
   - `{{risk}}` - 问题和风险

### 命令

```bash
python scripts/orchestrate_reports.py \
  --paths "E:\项目1,E:\项目2" \
  --time "本周" \
  --output "E:\周报" \
  --template "E:\周报模板.docx" \
  --format docx
```

### 输出

```
E:\周报\
├── tmp\                              # 临时文件（自动清理）
│   ├── time_result.json
│   ├── template_structure.json       # 模板结构分析
│   ├── week_01-task.json
│   └── ...
└── 第1周周报.docx                    # 最终周报（使用模板格式）
```

### 说明

- `--template "E:\周报模板.docx"`：提供Word模板文件路径
- `--format docx`：明确指定输出格式为Word
- 脚本会自动分析模板结构，识别需要填充的变量

---

## 示例3：批量生成多周周报

### 场景
批量生成一个时间范围内的所有周报，例如整个季度或半年。

### 命令

```bash
python scripts/orchestrate_reports.py \
  --paths "E:\A项目项目" \
  --time "2025-1-1-2025-3-31" \
  --output "E:\周报\2025年第一季度" \
  --template "E:\周报模板.docx" \
  --format docx
```

### 输出

```
E:\周报\2025年第一季度\
├── tmp\
│   ├── time_result.json              # 包含13周的数据
│   ├── template_structure.json
│   ├── week_01-task.json
│   ├── week_02-task.json
│   └── ...（共13周）
├── A项目第1周周报.docx
├── A项目第2周周报.docx
├── A项目第3周周报.docx
└── ...（共13个周报）
```

### 说明

- `--time "2025-1-1-2025-3-31"`：指定时间范围（1月1日到3月31日）
- 脚本自动按自然周划分时间范围
- 第一季度通常包含13-14周

---

## 示例4：多项目汇总

### 场景
将多个项目的Git提交记录汇总为一份周报，适用于同时负责多个项目的情况。

### 命令

```bash
python scripts/orchestrate_reports.py \
  --paths "E:\项目1,E:\项目2,E:\项目3" \
  --time "本周" \
  --output "E:\周报" \
  --template "E:\周报模板.docx" \
  --format docx
```

### 输出

```
E:\周报\
├── tmp\
│   ├── time_result.json
│   ├── template_structure.json
│   ├── week_01-task.json             # 包含3个项目路径
│   ├── week_01-log.json              # 包含3个项目的Git日志
│   └── week_01-report.json           # 汇总后的周报内容
└── A项目第1周周报.docx
```

### 说明

- `--paths "E:\项目1,E:\项目2,E:\项目3"`：多个项目路径用逗号分隔
- `get_git_logs.py` 会从所有项目获取Git日志并合并
- AI 清洗内容时会将所有项目的工作内容混合，**不按项目分组**

⚠️ **重要**：多项目汇总时，AI 会将所有项目的提交记录混合处理，不区分项目来源。如果需要按项目分组，请手动调整 `report-prompts.md` 中的清洗规则。

---

## 示例5：指定日期所在周

### 场景
生成某个日期所在周的周报，适用于临时补充某周的周报。

### 命令

```bash
python scripts/orchestrate_reports.py \
  --paths "E:\A项目项目" \
  --time "2025-1-15" \
  --output "E:\周报" \
  --template "E:\周报模板.docx" \
  --format docx
```

### 输出

```
E:\周报\
├── tmp\
│   ├── time_result.json
│   ├── template_structure.json
│   ├── week_01-task.json
│   └── ...
└── A项目第1周周报.docx                # 2025-01-13 至 2025-01-19
```

### 说明

- `--time "2025-1-15"`：指定单个日期
- 脚本自动计算该日期所在周（周一到周日）
- 2025-1-15 是周三，所在周是 2025-01-13（周一）至 2025-01-19（周日）

---

## 示例6：跳过二次确认

### 场景
在自动化脚本中使用周报生成器，不需要二次确认。

### 命令

```bash
python scripts/orchestrate_reports.py \
  --paths "E:\A项目项目" \
  --time "本周" \
  --output "E:\周报" \
  --template "E:\周报模板.docx" \
  --format docx \
  --no-confirm
```

### 说明

- `--no-confirm`：跳过二次确认，直接生成任务配置文件
- 适用于自动化脚本或CI/CD流程

---

## 示例7：生成本年所有周报

### 场景
年终总结时生成本年所有周报，用于年度汇报。

### 命令

```bash
python scripts/orchestrate_reports.py \
  --paths "E:\A项目项目" \
  --time "本年" \
  --output "E:\周报\2025年全年" \
  --template "E:\周报模板.docx" \
  --format docx
```

### 输出

```
E:\周报\2025年全年\
├── tmp\
│   ├── time_result.json              # 包含52周的数据
│   ├── template_structure.json
│   ├── week_01-task.json
│   ├── week_02-task.json
│   └── ...（共52周）
├── A项目第1周周报.docx
├── A项目第2周周报.docx
└── ...（共52个周报）
```

### 说明

- `--time "本年"`：自动解析本年1月1日到12月31日，并按自然周划分
- 一年通常包含52-53周

---

## 示例8：使用相对时间

### 场景
生成上周的周报，适用于每周一上班后快速生成上周周报。

### 命令

```bash
python scripts/orchestrate_reports.py \
  --paths "E:\A项目项目" \
  --time "上周" \
  --output "E:\周报" \
  --template "E:\周报模板.docx" \
  --format docx
```

### 说明

- `--time "上周"`：自动解析上周的周一到周日
- 每周一运行此命令，快速生成上周周报

---

## 时间表达式参考

| 表达式 | 说明 | 示例 |
|--------|------|------|
| `本周` | 当前周的周一到周日 | `--time "本周"` |
| `上周` | 上周的周一到周日 | `--time "上周"` |
| `本月` | 本月1日到最后一日（按周划分） | `--time "本月"` |
| `上月` | 上月1日到最后一日（按周划分） | `--time "上月"` |
| `本年` | 本年1月1日到12月31日（按周划分） | `--time "本年"` |
| `去年` | 去年1月1日到12月31日（按周划分） | `--time "去年"` |
| `YYYY-MM-DD` | 指定日期所在周 | `--time "2025-1-15"` |
| `YYYY-MM-DD-YYYY-MM-DD` | 指定时间范围（按周划分） | `--time "2025-1-1-2025-3-31"` |

---

## 常见错误及解决方法

### 错误1：路径包含空格

**错误信息**：`paths` 参数解析错误

**解决方法**：用双引号包裹路径
```bash
# ❌ 错误
--paths E:\My Project,E:\Another Project

# ✅ 正确
--paths "E:\My Project,E:\Another Project"
```

### 错误2：时间表达式包含空格

**错误信息**：`time` 参数解析错误

**解决方法**：用双引号包裹时间表达式
```bash
# ❌ 错误
--time 2025-1-1 - 2025-1-31

# ✅ 正确
--time "2025-1-1-2025-1-31"
```

### 错误3：模板文件不存在

**错误信息**：`template` 文件不存在

**解决方法**：检查模板文件路径是否正确
```bash
# 检查模板文件是否存在
ls "E:\周报模板.docx"

# 使用正确的路径
--template "E:\周报模板.docx"
```

---

## 下一步

- 📘 **[workflow.md](workflow.md)**：详细的工作流程指南
- 📘 **[script-api-reference.md](script-api-reference.md)**：Python 脚本详细调用参数
- 📘 **[report-prompts.md](report-prompts.md)**：内容清洗规则
