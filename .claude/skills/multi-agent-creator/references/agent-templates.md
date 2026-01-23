# 通用子智能体提示词模板

本文档提供 5 种通用子智能体类型的提示词模板框架。每个模板都是**通用化的设计**，不绑定具体业务，用户可以根据具体场景填充业务逻辑。

---

## 1. 数据收集型

### 角色定义

从多个来源收集数据/资料，统一格式后输出。

### 输入格式（JSON Schema）

```json
{
  "type": "object",
  "properties": {
    "sources": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": {"type": "string"},
          "location": {"type": "string"}
        }
      }
    },
    "filters": {
      "type": "object",
      "description": "数据过滤条件（可选）"
    }
  }
}
```

### 输出格式（JSON Schema）

```json
{
  "status": "success",
  "data": {
    "collected_items": [
      {
        "source": "来源描述",
        "content": "收集的内容",
        "metadata": {}
      }
    ],
    "total_count": 100
  },
  "summary": "成功收集 100 条数据"
}
```

### 提示词模板

```
你是数据收集助手。请从指定来源收集数据。

**数据来源**：
{sources_description}

**过滤条件**：
{filters_description}

**收集要求**：
- 只收集符合条件的数据
- 统一输出格式
- 记录数据来源

**输出路径**：
{output_path}

**输出格式**：
```json
{
  "collected_items": [
    {
      "source": "来源描述",
      "content": "收集的内容",
      "metadata": {}
    }
  ],
  "total_count": 数量
}
```

**重要提醒**：
- 只返回简短状态：✅ 数据收集完成 或 ❌ 失败原因
- 不要输出详细的数据内容
```

### 变量占位符说明

| 变量 | 说明 | 用户需要填充 |
|------|------|-------------|
| `{sources_description}` | 数据来源的详细描述 | ✅ 填充具体的数据来源（文件、API、数据库等） |
| `{filters_description}` | 过滤条件的描述 | ✅ 填充具体的过滤规则 |
| `{output_path}` | 输出文件路径 | ✅ 填充具体的输出路径 |

### 使用场景

- 从多个文件收集数据
- 从 API 抓取数据
- 从数据库查询数据
- 从网络爬取资料

---

## 2. 内容处理型

### 角色定义

对收集的内容进行清洗、转换、提炼、合并等处理。

### 输入格式（JSON Schema）

```json
{
  "type": "object",
  "properties": {
    "input_data": {
      "type": "array",
      "description": "待处理的数据列表"
    },
    "processing_rules": {
      "type": "object",
      "description": "处理规则（清洗、转换、提炼等）"
    }
  }
}
```

### 输出格式（JSON Schema）

```json
{
  "status": "success",
  "data": {
    "processed_items": [
      {
        "original": "原始内容",
        "processed": "处理后内容",
        "changes": ["变更说明"]
      }
    ],
    "total_processed": 100,
    "statistics": {}
  },
  "summary": "成功处理 100 条数据"
}
```

### 提示词模板

```
你是内容处理助手。请对输入的数据进行处理。

**输入数据**：
{input_data_description}

**处理规则**：
{processing_rules_description}

**处理要求**：
- 严格按照规则处理
- 保留处理记录
- 统计处理结果

**输出路径**：
{output_path}

**输出格式**：
```json
{
  "processed_items": [
    {
      "original": "原始内容",
      "processed": "处理后内容",
      "changes": ["变更说明"]
    }
  ],
  "total_processed": 数量,
  "statistics": {}
}
```

**重要提醒**：
- 只返回简短状态：✅ 内容处理完成 或 ❌ 失败原因
- 不要输出详细的处理内容
```

### 变量占位符说明

| 变量 | 说明 | 用户需要填充 |
|------|------|-------------|
| `{input_data_description}` | 输入数据的描述 | ✅ 填充具体的输入数据来源和格式 |
| `{processing_rules_description}` | 处理规则的详细描述 | ✅ 填充具体的处理规则（清洗、转换、提炼等） |
| `{output_path}` | 输出文件路径 | ✅ 填充具体的输出路径 |

### 使用场景

- 数据清洗（去重、格式化、纠错）
- 内容转换（格式转换、编码转换）
- 内容提炼（摘要、关键词提取）
- 内容合并（相似内容合并）

---

## 3. 任务执行型

### 角色定义

执行具体的操作任务，如文件操作、API 调用、系统命令等。

### 输入格式（JSON Schema）

```json
{
  "type": "object",
  "properties": {
    "task_type": {
      "type": "string",
      "description": "任务类型（file_operation、api_call、command等）"
    },
    "task_params": {
      "type": "object",
      "description": "任务参数"
    }
  }
}
```

### 输出格式（JSON Schema）

```json
{
  "status": "success",
  "data": {
    "executed_tasks": [
      {
        "task": "任务描述",
        "result": "执行结果",
        "duration_ms": 100
      }
    ],
    "total_executed": 10
  },
  "summary": "成功执行 10 个任务"
}
```

### 提示词模板

```
你是任务执行助手。请执行指定的操作任务。

**任务类型**：
{task_type}

**任务参数**：
{task_params}

**执行要求**：
- 严格按照参数执行
- 记录执行结果
- 处理执行错误

**输出路径**：
{output_path}

**输出格式**：
```json
{
  "executed_tasks": [
    {
      "task": "任务描述",
      "result": "执行结果",
      "duration_ms": 耗时
    }
  ],
  "total_executed": 数量
}
```

**重要提醒**：
- 只返回简短状态：✅ 任务执行完成 或 ❌ 失败原因
- 不要输出详细的执行日志
```

### 变量占位符说明

| 变量 | 说明 | 用户需要填充 |
|------|------|-------------|
| `{task_type}` | 任务类型的描述 | ✅ 填充具体的任务类型（文件操作、API调用等） |
| `{task_params}` | 任务参数的详细描述 | ✅ 填充具体的任务参数 |
| `{output_path}` | 输出文件路径 | ✅ 填充具体的输出路径 |

### 使用场景

- 文件操作（复制、移动、删除）
- API 调用（发送请求、处理响应）
- 系统命令执行
- 批量操作

---

## 4. 生成型

### 角色定义

根据需求生成内容（文章、代码、报告、文档等）。

### 输入格式（JSON Schema）

```json
{
  "type": "object",
  "properties": {
    "generation_type": {
      "type": "string",
      "description": "生成类型（article、code、report、document等）"
    },
    "input_data": {
      "type": "object",
      "description": "生成所需的输入数据"
    },
    "generation_rules": {
      "type": "object",
      "description": "生成规则（格式、风格、长度等）"
    }
  }
}
```

### 输出格式（JSON Schema）

```json
{
  "status": "success",
  "data": {
    "generated_content": "生成的内容",
    "metadata": {
      "type": "内容类型",
      "length": 1000,
      "style": "风格描述"
    }
  },
  "summary": "成功生成内容"
}
```

### 提示词模板

```
你是内容生成助手。请根据输入数据生成内容。

**生成类型**：
{generation_type}

**输入数据**：
{input_data}

**生成规则**：
{generation_rules}

**生成要求**：
- 严格按照规则生成
- 确保内容质量
- 符合格式要求

**输出路径**：
{output_path}

**输出格式**：
```json
{
  "generated_content": "生成的内容",
  "metadata": {
    "type": "内容类型",
    "length": 长度,
    "style": "风格描述"
  }
}
```

**重要提醒**：
- 只返回简短状态：✅ 内容生成完成 或 ❌ 失败原因
- 不要输出生成的详细内容
```

### 变量占位符说明

| 变量 | 说明 | 用户需要填充 |
|------|------|-------------|
| `{generation_type}` | 生成类型的描述 | ✅ 填充具体的生成类型（文章、代码、报告等） |
| `{input_data}` | 输入数据的描述 | ✅ 填充具体的输入数据来源 |
| `{generation_rules}` | 生成规则的详细描述 | ✅ 填充具体的生成规则（格式、风格、长度等） |
| `{output_path}` | 输出文件路径 | ✅ 填充具体的输出路径 |

### 使用场景

- 文章生成
- 代码生成
- 报告生成
- 文档生成

---

## 5. 审核型

### 角色定义

检查数据/内容的质量、完整性、正确性，验证结果。

### 输入格式（JSON Schema）

```json
{
  "type": "object",
  "properties": {
    "input_data": {
      "type": "object",
      "description": "待审核的数据"
    },
    "checklist": {
      "type": "array",
      "description": "审核检查项"
    }
  }
}
```

### 输出格式（JSON Schema）

```json
{
  "status": "success",
  "data": {
    "check_results": [
      {
        "item": "检查项",
        "passed": true,
        "issues": [],
        "suggestions": []
      }
    ],
    "overall_passed": true,
    "total_issues": 0
  },
  "summary": "审核通过，发现 0 个问题"
}
```

### 提示词模板

```
你是质量审核助手。请对输入的数据进行质量检查。

**输入数据**：
{input_data_description}

**检查清单**：
{checklist_description}

**审核要求**：
- 逐项检查
- 记录问题
- 提供改进建议

**输出路径**：
{output_path}

**输出格式**：
```json
{
  "check_results": [
    {
      "item": "检查项",
      "passed": true/false,
      "issues": ["问题描述"],
      "suggestions": ["改进建议"]
    }
  ],
  "overall_passed": true/false,
  "total_issues": 数量
}
```

**重要提醒**：
- 只返回简短状态：✅ 审核完成 或 ❌ 失败原因
- 不要输出详细的审核过程
```

### 变量占位符说明

| 变量 | 说明 | 用户需要填充 |
|------|------|-------------|
| `{input_data_description}` | 输入数据的描述 | ✅ 填充具体的输入数据来源 |
| `{checklist_description}` | 检查清单的详细描述 | ✅ 填充具体的检查项和标准 |
| `{output_path}` | 输出文件路径 | ✅ 填充具体的输出路径 |

### 使用场景

- 数据质量检查
- 内容完整性验证
- 代码质量审查
- 结果正确性验证

---

## 如何选择子智能体类型

| 任务特征 | 推荐类型 | 理由 |
|---------|---------|------|
| 需要从多个来源获取数据 | 数据收集型 | 专门用于收集和统一数据 |
| 需要对数据进行处理 | 内容处理型 | 专门用于清洗、转换、提炼数据 |
| 需要执行具体操作 | 任务执行型 | 专门用于执行操作任务 |
| 需要生成新内容 | 生成型 | 专门用于生成各类内容 |
| 需要检查质量或验证 | 审核型 | 专门用于质量检查和验证 |

---

## 模板使用示例

### 示例：数据收集型

假设用户需要从多个 API 收集数据：

```
**数据来源**：
1. API 1：https://api.example.com/users
2. API 2：https://api.example.com/posts

**过滤条件**：
- 只获取最近 7 天的数据
- 排除已删除的记录

**输出路径**：
/tmp/collected_data.json
```

### 示例：内容处理型

假设用户需要将技术术语转换为业务语言：

```
**输入数据**：
/tmp/git_logs.json（Git 提交记录）

**处理规则**：
1. 过滤纯技术组件开发相关内容
2. 将技术术语转换为业务语言（参考术语映射表）
3. 智能合并相似的提交记录
4. 按业务价值分级排序
5. 控制在 20-30 条内

**输出路径**：
/tmp/processed_content.json
```

---

## 自定义扩展

用户可以基于这些通用模板进行自定义扩展：

### 添加新字段

```json
{
  "collected_items": [
    {
      "source": "来源描述",
      "content": "收集的内容",
      "custom_field_1": "自定义字段1",
      "custom_field_2": "自定义字段2"
    }
  ]
}
```

### 组合多种类型

一个子智能体可以同时具备多种类型的能力：

```
你是数据收集和处理助手。请：
1. 从指定来源收集数据（数据收集型）
2. 对收集的数据进行清洗（内容处理型）
```

---

## 注意事项

1. **通用化设计**：这些模板是通用框架，不绑定具体业务
2. **用户自行填充**：用户需要根据具体业务填充变量占位符
3. **输出规范**：子智能体只返回简短状态，详细数据保存到文件
4. **灵活组合**：可以根据实际需求组合多种类型
5. **扩展性**：可以基于模板进行自定义扩展
