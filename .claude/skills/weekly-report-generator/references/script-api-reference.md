# Python 脚本 API 参考手册

本文档提供所有 Python 脚本的详细调用参数说明和使用示例。

根据第一周实战经验，以下是各个Python脚本的**正确调用方式**和**参数说明**。

---

## 1. parse_time.py - 智能时间解析

**功能**：解析各种时间表达式（相对时间、绝对时间范围、单个日期），自动按自然周（周一到周日）划分时间范围，生成标准化的周任务清单数据。

**调用示例**（相对时间）：
```bash
# 解析"本周"
python scripts/parse_time.py \
  --expression "本周" \
  --output "E:\工作\study\results\time_result.json"

# 解析"上周"
python scripts/parse_time.py \
  --expression "上周" \
  --output "E:\工作\study\results\time_result.json"

# 解析"本月"
python scripts/parse_time.py \
  --expression "本月" \
  --output "E:\工作\study\results\time_result.json"
```

**调用示例**（绝对时间范围）：
```bash
# 解析时间范围（支持多种分隔符：- . / ~ ～）
python scripts/parse_time.py \
  --expression "2025.1.10-2025.1.15" \
  --output "E:\工作\study\results\time_result.json"

python scripts/parse_time.py \
  --expression "2025/1/10～2025/1/15" \
  --output "E:\工作\study\results\time_result.json"
```

**调用示例**（单个日期）：
```bash
# 解析单个日期，自动计算所在周
python scripts/parse_time.py \
  --expression "2025.1.15" \
  --output "E:\工作\study\results\time_result.json"
```

**参数说明**：
- `--expression`：时间表达式（必需，支持以下格式）
  - 相对时间：`本周`、`上周`、`本月`、`上月`、`本年`、`去年`
  - 绝对时间范围：`YYYY-M-D-YYYY-M-D` 或 `YYYY.M.D-YYYY.M.D` 或 `YYYY/M/D～YYYY/M/D`
  - 单个日期：`YYYY-M-D`（自动计算所在周）
- `--output`：输出JSON文件路径（可选，不提供则打印到控制台）

**输出格式**：
```json
{
  "success": true,
  "expression": "本周",
  "start_date": "2025-01-13",
  "end_date": "2025-01-17",
  "start_weekday": "周一",
  "end_weekday": "周五",
  "weeks": [
    {"week": 1, "start": "2025-01-13", "end": "2025-01-17"},
    {"week": 2, "start": "2025-01-20", "end": "2025-01-24"}
  ],
  "total_weeks": 2,
  "description": "2025年01月13日(周一)至2025年01月17日(周五)"
}
```

**字段说明**：
- `success`：解析是否成功
- `expression`：原始时间表达式
- `start_date`/`end_date`：解析后的时间范围
- `start_weekday`/`end_weekday`：开始和结束日期是星期几
- `weeks`：按自然周划分的数组（每个元素包含week、start、end）
- `total_weeks`：总周数
- `description`：用户友好的时间范围描述

**常见错误**：
- ❌ `2025-1-10 ~ 2025-1-15`（有空格）→ ✅ `2025-1-10-2025-1-15`（无空格）
- ❌ `本周 到 下周`（中文范围表达）→ ✅ `本周`（只支持单个相对时间表达）
- ❌ `2025/1/10-2025/1/15`（混合分隔符）→ ✅ `2025/1/10-2025/1/15`（统一分隔符）

**Windows兼容性**：
- ✅ 支持UTF-8编码输出
- ✅ 支持多种日期分隔符（- . /）
- ✅ 友好的中文错误提示

**使用场景**：
- 主智能体在Step 1中调用，解析用户输入的时间表达式
- 自动计算需要生成多少份周报
- 提供每周的start和end日期给子智能体

---

## 2. calculate_weeks.py - 计算周数并生成任务清单（已废弃，使用parse_time.py替代）

**功能**：将时间范围按周一到周日划分为N周，生成tasks.json任务清单。

**调用示例**：
```bash
python scripts/calculate_weeks.py \
  --start "2025-05-12" \
  --end "2026-01-16" \
  --output "E:\工作\study\results\tasks.json"
```

**参数说明**：
- `--start`：开始日期（YYYY-MM-DD格式，必需）
- `--end`：结束日期（YYYY-MM-DD格式，必需）
- `--output`：输出JSON文件路径（必需）

**输出格式**：生成包含N周任务的tasks.json文件

---

## 3. analyze_template.py - 解析Word模板结构

**功能**：分析Word模板的章节结构和变量定义，生成template_structure.json。

**调用示例**：
```bash
python scripts/analyze_template.py \
  --template "E:\工作\study\report.docx" \
  --output "E:\工作\study\results\template_structure.json"
```

**参数说明**：
- `--template`：Word模板文件路径（.docx格式，必需）
- `--output`：输出JSON文件路径（必需）

**输出格式**：生成包含模板结构信息的JSON文件

---

## 4. get_git_logs.py - 获取Git提交日志

**功能**：从单个或多个Git仓库获取指定时间范围的提交记录，按星期几分组。

**调用示例**（单个仓库）：
```bash
python scripts/get_git_logs.py \
  --paths "E:\工作\pulian\A-ui" \
  --since "2025-05-12" \
  --until "2025-05-18" \
  --output "E:\工作\study\results\week_1_data.json"
```

**调用示例**（多个仓库）：
```bash
python scripts/get_git_logs.py \
  --paths "E:\工作\pulian\A-ui,E:\工作\pulian\GroupSideProjectManagementSystem" \
  --since "2025-05-12" \
  --until "2025-05-18" \
  --output "E:\工作\study\results\week_1_data.json"
```

**参数说明**：
- `--paths`：项目路径列表，**用逗号分隔**（必需，⚠️ 注意是paths不是repos）
- `--since`：开始日期（YYYY-MM-DD格式，必需，⚠️ 注意是since不是start）
- `--until`：结束日期（YYYY-MM-DD格式，必需，⚠️ 注意是until不是end）
- `--output`：输出JSON文件路径（可选，但推荐提供以避免控制台编码问题）
- `--no-minimal`：关闭精简模式，输出完整信息（包含hash、author、email等字段，可选）
- `--split-by-week`：按周分割数据（可选，用于批量场景）

**常见错误**：
- ❌ `--repos "path1,path2"` → ✅ `--paths "path1,path2"`
- ❌ `--start "2025-05-12"` → ✅ `--since "2025-05-12"`
- ❌ `--end "2025-05-18"` → ✅ `--until "2025-05-18"`

**输出格式**：生成包含按星期几分组的提交记录的JSON文件

---

## 5. fill_template.py - 填充Word模板

**功能**：使用JSON数据填充Word模板，生成最终的周报文档。

**调用示例**：
```bash
python scripts/fill_template.py \
  --template "E:\工作\study\report\report.docx" \
  --data "E:\工作\study\results\week_1_fill_data.json" \
  --output "E:\工作\study\results" \
  --filename "A项目第一周周报.docx"
```

**参数说明**：
- `--template`：Word模板文件路径（.docx格式，必需）
- `--data`：填充数据JSON文件路径（必需）
- `--output`：输出目录路径（必需，⚠️ 是目录不是完整文件路径）
- `--filename`：输出文件名（必需，⚠️ 这个参数容易遗漏）

**数据格式**：填充数据JSON必须与模板章节对应，例如：
```json
{
  "本周工作情况：": "1. 完成功能A\n2. 完成功能B",
  "下周工作计划：": "1. 继续优化A\n2. 测试B",
  "需协调解决问题：": "暂无"
}
```

**常见错误**：
- ❌ 遗漏 `--filename` 参数
- ❌ `--output` 传入完整文件路径 → ✅ `--output` 传入目录路径，`--filename` 传入文件名

**输出格式**：生成填充完成后的Word文档（.docx格式）

---

## 6. export_report.py - 导出Markdown周报

**功能**：将清洗后的内容导出为Markdown格式的周报。

**调用示例**：
```bash
python scripts/export_report.py \
  --content "清洗后的周报内容" \
  --output "E:\工作\study\results\week_1.md"
```

**参数说明**：
- `--content`：周报内容（Markdown格式，必需）
- `--output`：输出文件路径（必需）

**使用场景**：当用户不需要Word模板，只需要Markdown格式时使用。

---

## 7. update_task_status.py - 更新任务状态

**功能**：更新tasks.json中指定任务的执行状态。

**调用示例**：
```bash
python scripts/update_task_status.py \
  --tasks "results/tasks.json" \
  --week 1 \
  --status "completed"
```

**参数说明**：
- `--tasks`：tasks.json文件路径（必需）
- `--week`：周数（从1开始，必需）
- `--status`：任务状态（必需，可选值：pending/in_progress/completed/failed）
- `--error`：错误信息（可选，当status为failed时提供）

**使用场景**：在批量生成过程中，用于跟踪每个任务的执行状态。

---

## 脚本调用流程示例（完整版）

### 单周周报生成流程（主智能体 + 子智能体）

```bash
# 主智能体执行：Step 1 数据准备和验证

# Step 1.1: 解析时间表达式（推荐使用parse_time.py）
python scripts/parse_time.py \
  --expression "2025-05-12-2025-05-18" \
  --output "results/time_result.json"

# Step 1.2: 解析模板（可选）
python scripts/analyze_template.py \
  --template "report.docx" \
  --output "results/template_structure.json"

# 子智能体执行：Step 2 完整生成周报（独立完成）

# Step 2.1: 获取Git日志
python scripts/get_git_logs.py \
  --paths "E:\proj1,E:\proj2" \
  --since "2025-05-12" \
  --until "2025-05-18" \
  --output "results/tmp/week_1-log.json"

# Step 2.2: AI清洗内容（AI执行，非脚本）
# - 读取 week_1-log.json
# - 根据 report-prompts.md 清洗内容
# - 生成 week_1-report.json（包含清洗后内容和补充章节）

# Step 2.3: AI填充模板（AI执行，非脚本）
# - 读取 template_structure.json
# - 读取 week_1-report.json
# - 填充模板内容

# Step 2.4: 导出Word文档
python scripts/fill_template.py \
  --template "report.docx" \
  --data "results/tmp/week_1-fill-data.json" \
  --output "results" \
  --filename "周报20250512-20250518.docx"
```

### 多周周报生成流程（并行子智能体）

```bash
# 主智能体执行：Step 1 数据准备和验证

# Step 1.1: 解析时间表达式
python scripts/parse_time.py \
  --expression "本月" \
  --output "results/time_result.json"

# Step 1.2: 解析模板
python scripts/analyze_template.py \
  --template "report.docx" \
  --output "results/template_structure.json"

# 主智能体：Step 2 并行启动子智能体
# 读取 time_result.json 中的 weeks 数组
# 为每个 week 启动一个子智能体（使用Task工具）

# 子智能体执行：独立完成每个周报
# 对于每个 week：
#   1. 调用 get_git_logs.py（使用week的start和end）
#   2. 创建 week_XX-log.json（保存Git日志）
#   3. AI清洗内容并生成 week_XX-report.json
#   4. AI补充主智能体指定的章节
#   5. AI填充模板
#   6. 调用 fill_template.py 或 export_report.py 导出文件
#   7. 返回成功/失败状态

# 主智能体执行：Step 3 结果汇总和清理
# 汇总所有子智能体的返回结果
# 清理临时文件（成功任务的临时文件删除，失败任务的保留）
```

---

## 参数对照表（避免混淆）

| 功能 | 错误参数 | 正确参数 | 说明 |
|------|---------|---------|------|
| 时间解析 | ❌ | `--expression` | 支持相对时间、绝对范围、单个日期 |
| Git日志仓库 | `--repos` | `--paths` | 多个仓库用逗号分隔 |
| Git日志开始日期 | `--start` | `--since` | YYYY-MM-DD格式 |
| Git日志结束日期 | `--end` | `--until` | YYYY-MM-DD格式 |
| 模板填充输出 | 完整路径 | `--output`目录 + `--filename`文件名 | 分开传递 |
| ~~周数计算开始日期~~ | ❌ | `--start` | ⚠️ calculate_weeks.py已废弃，使用parse_time.py |
| ~~周数计算结束日期~~ | ❌ | `--end` | ⚠️ calculate_weeks.py已废弃，使用parse_time.py |

**重要提醒**：
- ✅ **推荐使用 `parse_time.py`**（支持相对时间、自动按周划分）
- ⚠️ `get_git_logs.py` 使用 `--since/--until`
- ⚠️ `calculate_weeks.py` 已废弃，使用 `parse_time.py` 替代
- ⚠️ `fill_template.py` 需要同时提供 `--output`（目录）和 `--filename`（文件名）

**parse_time.py 时间表达式格式**：
- 相对时间：`本周`、`上周`、`本月`、`上月`、`本年`、`去年`
- 绝对范围：`2025-1-10-2025-1-15`（支持 `-` `/` `.` `~` `～` 分隔符）
- 单个日期：`2025-1-15`（自动计算所在周）
