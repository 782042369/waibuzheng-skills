# 周报生成工作流程

本文档详细说明周报生成的完整工作流程，包括主智能体和子智能体的职责划分、子智能体提示模板、以及临时文件结构。

---

## 工作流程概览

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: 主智能体运行编排脚本（orchestrate_reports.py）        │
│ - 解析时间表达式                                              │
│ - 验证项目路径和输出路径                                      │
│ - 分析模板文件结构                                            │
│ - 为每个周生成独立任务配置文件                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: 主智能体创建任务清单（TodoWrite）                     │
│ - 为每个周创建独立任务                                        │
│ - 设置初始状态为 pending                                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: 主智能体并行启动子智能体                              │
│ - 读取 {输出路径}/tmp/claude_instruction.md                 │
│ - 为每个周启动独立的 general-purpose 子智能体                │
│ - 更新任务状态（in_progress → completed）                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: 子智能体独立完成每个周报                              │
│ - 获取Git日志                                                │
│ - AI清洗内容并转换为业务语言                                  │
│ - 补充下周计划和问题章节                                      │
│ - 填充模板并导出周报                                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 5: 主智能体汇总结果并清理临时文件                        │
│ - 收集所有子任务的成功/失败状态                               │
│ - 标记所有任务为 completed                                   │
│ - 删除成功的临时文件，保留失败的用于调试                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 3 详细说明：并行处理每个周报

### 3.1 创建任务清单并读取调用说明

**第一步：创建任务清单**（必须）

在开始处理周报前，主智能体**必须**使用 TodoWrite 工具创建任务清单：

```python
TodoWrite(
  todos = [
    {"content": "读取调用说明和参考文档", "status": "pending", "activeForm": "读取调用说明和参考文档"},
    {"content": "为第1周启动子智能体", "status": "pending", "activeForm": "为第1周启动子智能体"},
    {"content": "为第2周启动子智能体", "status": "pending", "activeForm": "为第2周启动子智能体"},
    # ... 为每个周创建一个任务
    {"content": "汇总所有结果并清理临时文件", "status": "pending", "activeForm": "汇总所有结果并清理临时文件"}
  ]
)
```

**重要**：
- 根据实际周数动态创建任务清单
- 每个周一个独立任务
- 启动子任务时标记为 `in_progress`
- 完成后立即标记为 `completed`

**第二步：读取调用说明**

主智能体首先读取 `{输出路径}/tmp/claude_instruction.md`，获取：
- 生成的周数
- 每个周的时间范围
- 项目路径列表
- 模板文件路径（如果提供）
- 每个周的任务配置文件路径

**标记第一个任务为 in_progress**

### 3.2 并行启动子智能体

主智能体使用 **Task 工具**为每个周启动独立的 `general-purpose` 子智能体。

**调用方式**（使用 Task 工具）：

```
对于每个周（例如第1周），调用：

# 标记当前任务为 in_progress
TodoWrite(todos=[...], current_task_index=1)  # "为第1周启动子智能体" → in_progress

Task(
  subagent_type="general-purpose",
  prompt="<替换变量后的子智能体任务提示>",
  description="生成第{week_num}周周报"
)

# 任务完成后立即标记为 completed
TodoWrite(todos=[...], current_task_index=1)  # "为第1周启动子智能体" → completed
```

**并行启动示例**（假设有3个周报需要生成）：

```
Task(
  subagent_type="general-purpose",
  prompt="你是周报生成助手。请独立完成第 1 周周报的生成任务。\n\n**重要信息**：\n- 输出文件名必须是：A项目第1周周报.docx\n- 时间范围：2025-01-13 至 2025-01-17\n\n**任务步骤**：\n\n1. **读取任务配置**：\n   文件路径：E:/周报/tmp/week_1-task.json\n\n2. **获取Git日志**：\n   调用脚本：scripts/get_git_logs.py\n   参数：--paths \"E:/A项目项目\" --since 2025-01-13 --until 2025-01-17 --output \"E:/周报/tmp/week_1-log.json\"\n\n3. **读取Git日志并清洗内容**（必须严格执行）：\n   - 读取清洗规则：references/report-prompts.md\n   - 读取Git日志：E:/周报/tmp/week_1-log.json\n   - 严格按照清洗规则处理：\n     * 过滤纯技术组件开发、底层技术实现、开发工具相关内容\n     * 将技术术语转换为业务语言\n     * 智能合并相似的提交记录\n     * 按业务价值分级排序\n     * 控制在20-30条内\n   - 输出清洗后的工作内容\n\n4. **保存清洗后的内容**：\n   ⚠️ **必须使用以下JSON格式**：\n   ```json\n   {\n     \"title\": \"A项目第1周周报（2025-01-13 至 2025-01-17）\",\n     \"sections\": [\n       {\n         \"title\": \"本周工作情况：\",\n         \"content\": \"1. 第一条工作内容\\n2. 第二条工作内容\\n3. 第三条工作内容\\n...\"\n       },\n       {\n         \"title\": \"下周工作计划：\",\n         \"content\": \"1. 第一项计划\\n2. 第二项计划\\n3. 第三项计划\\n...\"\n       },\n       {\n         \"title\": \"需协调解决问题：\",\n         \"content\": \"1. 第一个问题\\n2. 第二个问题\\n3. 第三个问题\\n...\"\n       }\n     ]\n   }\n   ```\n   ⚠️ **重要提醒**：\n   - 必须使用 `sections` 结构，不要使用 `work_items`、`content`、`future_plan` 等其他字段名\n   - `content` 字段必须是字符串，用换行符（\\n）分隔多条目\n   - 不要使用数组格式，必须转换为字符串\n\n   保存到：E:/周报/tmp/week_1-report.json\n\n5. **补充下周计划和问题章节**（必须）：\n   - 基于清洗后的工作内容推导下周计划\n   - 基于工作内容识别问题和风险\n   - 更新 week_1-report.json\n\n6. **填充模板并导出**：\n   调用脚本：scripts/fill_template.py\n   参数：--template \"E:/周报模板.docx\" --data \"E:/周报/tmp/week_1-report.json\" --output \"E:/周报/A项目第1周周报.docx\"\n\n**重要提醒**：\n- 必须严格遵守清洗规则，技术术语必须转换为业务语言\n- 必须补充下周计划和问题章节\n- 输出文件名必须正确\n- ⚠️ **JSON格式必须使用 sections 结构**\n\n完成后返回：✅ 第1周周报生成成功 或 ❌ 失败原因",
  description="生成第1周周报"
)
```

**重要**：
- 如果有多个周报，在**同一个响应中**调用多次 Task 工具（并行执行）
- 每次调用都需要替换 `{week_num}`、`{start_date}`、`{end_date}`、`{output_path}`、`{project1}`、`{template_path}` 等变量
- 使用 `{output_path}/tmp/claude_instruction.md` 中提供的具体变量值

---

**子智能体任务提示模板**（需要替换变量后使用）：

```
你是周报生成助手。请独立完成第 {week_num} 周周报的生成任务。

**重要信息**：
- 输出文件名必须是：A项目第{week_num}周周报.docx
- 时间范围：{start_date} 至 {end_date}

**任务步骤**：

1. **读取任务配置**：
   文件路径：{output_path}/tmp/week_{week_num}-task.json

2. **获取Git日志**：
   调用脚本：scripts/get_git_logs.py
   参数：--paths "{project1},{project2}" --since {start_date} --until {end_date} --output "{output_path}/tmp/week_{week_num}-log.json"

3. **读取Git日志并清洗内容**（必须严格执行）：
   - 读取清洗规则：references/report-prompts.md
   - 读取Git日志：{output_path}/tmp/week_{week_num}-log.json
   - 严格按照清洗规则处理：
     * 过滤纯技术组件开发、底层技术实现、开发工具相关内容
     * 将技术术语转换为业务语言
     * 智能合并相似的提交记录
     * 按业务价值分级排序
     * 控制在20-30条内
   - 输出清洗后的工作内容

4. **保存清洗后的内容**：
   ⚠️ **必须使用以下JSON格式**：
   ```json
   {
     "title": "A项目第{week_num}周周报（{start_date} 至 {end_date}）",
     "sections": [
       {
         "title": "本周工作情况：",
         "content": "1. 第一条工作内容\n2. 第二条工作内容\n3. 第三条工作内容\n..."
       },
       {
         "title": "下周工作计划：",
         "content": "1. 第一项计划\n2. 第二项计划\n3. 第三项计划\n..."
       },
       {
         "title": "需协调解决问题：",
         "content": "1. 第一个问题\n2. 第二个问题\n3. 第三个问题\n..."
       }
     ]
   }
   ```
   ⚠️ **重要提醒**：
   - 必须使用 `sections` 结构，不要使用 `work_items`、`content`、`future_plan` 等其他字段名
   - `content` 字段必须是字符串，用换行符（\n）分隔多条目
   - 不要使用数组格式，必须转换为字符串

   保存到：{output_path}/tmp/week_{week_num}-report.json

5. **补充下周计划和问题章节**（必须）：
   - 基于清洗后的工作内容推导下周计划
   - 基于工作内容识别问题和风险
   - 更新 week_{week_num}-report.json

6. **填充模板并导出**：
   调用脚本：scripts/fill_template.py
   参数：--template "{template_path}" --data "{output_path}/tmp/week_{week_num}-report.json" --output "{output_path}/A项目第{week_num}周周报.docx"

**重要提醒**：
- 必须严格遵守清洗规则，技术术语必须转换为业务语言
- 必须补充下周计划和问题章节
- 输出文件名必须正确
- ⚠️ **JSON格式必须使用 sections 结构**

完成后返回：✅ 第{week_num}周周报生成成功 或 ❌ 失败原因
```

**模板变量说明**：
- `{week_num}`：周数（1, 2, 3, ...）
- `{start_date}`：开始日期（YYYY-MM-DD）
- `{end_date}`：结束日期（YYYY-MM-DD）
- `{output_path}`：输出目录路径
- `{project1},{project2}`：项目路径列表（逗号分隔）
- `{template_path}`：模板文件路径

### 3.3 汇总结果

**标记汇总任务为 in_progress**：
```python
TodoWrite(todos=[...], current_task_index=last)  # 最后一个任务 → in_progress
```

主智能体收集所有子智能体的返回结果：
- ✅ 成功：记录成功状态
- ❌ 失败：记录失败原因

### 3.4 清理临时文件

主智能体清理临时文件：
- **成功的任务**：删除对应的 `week_XX-task.json`、`week_XX-log.json`、`week_XX-report.json`
- **失败的任务**：保留所有临时文件，用于调试

**标记所有任务为 completed**：
```python
TodoWrite(todos=[...], all_completed=True)  # 所有任务 → completed
```

---

## 临时文件结构

```
{输出路径}/
├── tmp/
│   ├── time_result.json              # 时间解析结果
│   ├── template_structure.json       # 模板结构（如果提供模板）
│   ├── claude_instruction.md         # Claude Code 调用说明
│   ├── week_01-task.json             # 第1周任务配置
│   ├── week_01-log.json              # 第1周Git日志（子智能体生成）
│   ├── week_01-report.json           # 第1周清洗后内容（子智能体生成）
│   ├── week_02-task.json             # 第2周任务配置
│   ├── week_02-log.json              # 第2周Git日志（子智能体生成）
│   ├── week_02-report.json           # 第2周清洗后内容（子智能体生成）
│   └── ...                           # 更多周
├── A项目第1周周报.docx                # 第1周最终周报
├── A项目第2周周报.docx                # 第2周最终周报
└── ...                               # 更多周报
```

---

## 重要注意事项

### 主智能体职责

- ✅ 运行 `orchestrate_reports.py` 准备数据
- ✅ 读取并理解 `claude_instruction.md`
- ✅ 并行启动子智能体
- ✅ 汇总子智能体结果
- ✅ 清理临时文件
- ❌ **不执行实际的周报生成工作**

### 子智能体职责

- ✅ 读取任务配置文件
- ✅ 调用 `get_git_logs.py` 获取Git日志
- ✅ AI清洗内容并转换为业务语言
- ✅ 补充下周计划和问题章节
- ✅ 调用 `fill_template.py` 填充模板
- ✅ 返回成功/失败状态
- ❌ **不调用其他脚本或修改工作流程**

### 内容清洗（重要）

子智能体**必须**严格执行内容清洗规则：
1. **读取** `references/report-prompts.md`
2. **过滤**纯技术组件开发、底层技术实现、开发工具相关内容
3. **转换**技术术语为业务语言（参考术语映射表）
4. **合并**相似的提交记录
5. **排序**按业务价值分级
6. **控制**在20-30条内

### JSON格式要求

子智能体保存清洗后的内容时，**必须**使用以下格式：

```json
{
  "title": "周报标题",
  "sections": [
    {
      "title": "章节标题",
      "content": "1. 第一条\n2. 第二条\n3. 第三条"
    }
  ]
}
```

⚠️ **重要**：
- 使用 `sections` 字段，不要使用 `work_items`、`content`、`future_plan` 等其他字段名
- `content` 字段必须是字符串，用 `\n` 分隔多条目
- 不要使用数组格式

---

## 故障排查

### 子智能体失败

如果某个子智能体失败：
1. 查看子智能体返回的错误信息
2. 检查 `{输出路径}/tmp/week_XX-task.json` 是否正确
3. 检查 `{输出路径}/tmp/week_XX-log.json` 是否包含有效Git日志
4. 检查 `{输出路径}/tmp/week_XX-report.json` 是否符合JSON格式要求

### JSON格式错误

如果 `fill_template.py` 报错：
1. 检查 `sections` 字段是否存在
2. 检查 `content` 字段是否为字符串（不是数组）
3. 检查换行符是否使用 `\n` 而不是 `\n`

### 内容清洗不完整

如果周报包含过多技术术语：
1. 检查子智能体是否读取了 `references/report-prompts.md`
2. 检查子智能体是否严格执行了清洗规则
3. 调整清洗规则中的术语映射表

---

## 示例：单周周报生成

```bash
# Step 1: 主智能体运行编排脚本
python scripts/orchestrate_reports.py \
  --paths "E:\A项目项目" \
  --time "本周" \
  --output "E:\周报" \
  --template "E:\周报模板.docx" \
  --format docx

# Step 2: 主智能体读取调用说明
# 读取 E:\周报\tmp\claude_instruction.md

# Step 3: 主智能体启动子智能体（使用Task工具）
# 复制子智能体任务提示模板，替换变量：
# {week_num}=1, {start_date}=2025-01-13, {end_date}=2025-01-17
# {output_path}=E:\周报, {project1}=E:\A项目项目
# {template_path}=E:\周报模板.docx

# Step 4: 子智能体完成任务
# 返回：✅ 第1周周报生成成功

# Step 5: 主智能体清理临时文件
# 删除 E:\周报\tmp\week_01-*.json
```
