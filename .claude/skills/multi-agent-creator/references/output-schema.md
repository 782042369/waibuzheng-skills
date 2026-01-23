# 通用输出规范

本文档定义所有子智能体的统一输出格式规范，确保主智能体能够统一处理子智能体的输出。

---

## 核心原则

1. **简短输出**：子智能体只返回简短的成功/失败状态
2. **详细数据**：详细数据保存到文件，不在响应中输出
3. **统一格式**：所有子智能体遵循相同的输出格式
4. **明确状态**：使用明确的状态码和错误码

---

## 基本输出格式

### 成功输出

```json
{
  "status": "success",
  "data": {
    // 具体业务数据
  },
  "summary": "简短的成功描述"
}
```

**子智能体响应**：
```
✅ 任务完成
```

### 失败输出

```json
{
  "status": "failed",
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {}
  },
  "suggestion": "恢复建议"
}
```

**子智能体响应**：
```
❌ 任务失败：错误原因
```

---

## 状态码定义

| 状态码 | 说明 | 使用场景 |
|--------|------|---------|
| `success` | 成功 | 任务正常完成 |
| `failed` | 失败 | 任务执行失败 |
| `partial` | 部分成功 | 部分任务成功，部分失败 |
| `timeout` | 超时 | 任务执行超时 |
| `invalid_input` | 输入无效 | 输入数据格式错误或不完整 |

---

## 错误码定义

### 通用错误码

| 错误码 | 说明 | 示例 |
|--------|------|------|
| `INPUT_NOT_FOUND` | 输入文件不存在 | 输入文件 /path/to/file.json 不存在 |
| `INPUT_INVALID` | 输入格式无效 | 输入数据不是有效的 JSON 格式 |
| `OUTPUT_ERROR` | 输出失败 | 无法写入输出文件 /path/to/output.json |
| `TIMEOUT` | 执行超时 | 任务执行超过 60 秒 |
| `UNKNOWN_ERROR` | 未知错误 | 发生未预期的错误 |

### 数据收集型错误码

| 错误码 | 说明 | 示例 |
|--------|------|------|
| `SOURCE_UNREACHABLE` | 数据源不可达 | 无法连接到 API https://api.example.com |
| `SOURCE_EMPTY` | 数据源为空 | 数据源返回空结果 |
| `FILTER_FAILED` | 过滤失败 | 无法应用过滤条件 |

### 内容处理型错误码

| 错误码 | 说明 | 示例 |
|--------|------|------|
| `PROCESSING_FAILED` | 处理失败 | 无法处理数据：字段缺失 |
| `TRANSFORMATION_ERROR` | 转换错误 | 无法转换数据格式 |

### 任务执行型错误码

| 错误码 | 说明 | 示例 |
|--------|------|------|
| `EXECUTION_FAILED` | 执行失败 | 命令执行失败：exit code 1 |
| `PERMISSION_DENIED` | 权限不足 | 无权限访问文件 /path/to/file |

### 生成型错误码

| 错误码 | 说明 | 示例 |
|--------|------|------|
| `GENERATION_FAILED` | 生成失败 | 无法生成内容：输入数据不足 |
| `FORMAT_INVALID` | 格式无效 | 输出格式不符合要求 |

### 审核型错误码

| 错误码 | 说明 | 示例 |
|--------|------|------|
| `CHECK_FAILED` | 检查失败 | 无法完成质量检查 |
| `VALIDATION_ERROR` | 验证错误 | 数据验证失败 |

---

## 完整 JSON Schema

### 成功输出 Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["status", "data", "summary"],
  "properties": {
    "status": {
      "type": "string",
      "enum": ["success", "partial"]
    },
    "data": {
      "type": "object",
      "description": "具体业务数据，由各子智能体类型定义"
    },
    "summary": {
      "type": "string",
      "description": "简短的成功描述"
    },
    "metadata": {
      "type": "object",
      "description": "元数据（可选）",
      "properties": {
        "timestamp": {
          "type": "string",
          "format": "date-time"
        },
        "duration_ms": {
          "type": "number",
          "description": "执行耗时（毫秒）"
        },
        "version": {
          "type": "string",
          "description": "子智能体版本"
        }
      }
    }
  }
}
```

### 失败输出 Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["status", "error"],
  "properties": {
    "status": {
      "type": "string",
      "enum": ["failed", "timeout", "invalid_input"]
    },
    "error": {
      "type": "object",
      "required": ["code", "message"],
      "properties": {
        "code": {
          "type": "string",
          "description": "错误码"
        },
        "message": {
          "type": "string",
          "description": "错误描述"
        },
        "details": {
          "type": "object",
          "description": "错误详情（可选）"
        }
      }
    },
    "suggestion": {
      "type": "string",
      "description": "恢复建议（可选）"
    }
  }
}
```

---

## 各子智能体类型的输出格式

### 1. 数据收集型

#### 成功输出

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
  "summary": "成功收集 100 条数据",
  "metadata": {
    "timestamp": "2025-01-22T10:00:00Z",
    "duration_ms": 1500
  }
}
```

#### 失败输出

```json
{
  "status": "failed",
  "error": {
    "code": "SOURCE_UNREACHABLE",
    "message": "无法连接到 API https://api.example.com",
    "details": {
      "url": "https://api.example.com",
      "http_status": 503
    }
  },
  "suggestion": "检查网络连接或稍后重试"
}
```

### 2. 内容处理型

#### 成功输出

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
    "statistics": {
      "removed_duplicates": 5,
      "fixed_errors": 3
    }
  },
  "summary": "成功处理 100 条数据，移除 5 条重复，修复 3 个错误"
}
```

#### 失败输出

```json
{
  "status": "failed",
  "error": {
    "code": "PROCESSING_FAILED",
    "message": "无法处理数据：字段缺失",
    "details": {
      "field": "content",
      "index": 42
    }
  },
  "suggestion": "检查输入数据的完整性"
}
```

### 3. 任务执行型

#### 成功输出

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
    "total_executed": 10,
    "total_duration_ms": 1000
  },
  "summary": "成功执行 10 个任务，总耗时 1 秒"
}
```

#### 失败输出

```json
{
  "status": "failed",
  "error": {
    "code": "EXECUTION_FAILED",
    "message": "命令执行失败：exit code 1",
    "details": {
      "command": "python script.py",
      "exit_code": 1
    }
  },
  "suggestion": "检查命令参数或脚本逻辑"
}
```

### 4. 生成型

#### 成功输出

```json
{
  "status": "success",
  "data": {
    "generated_content": "生成的内容",
    "metadata": {
      "type": "article",
      "length": 2500,
      "style": "专业"
    }
  },
  "summary": "成功生成 2500 字的专业文章"
}
```

#### 失败输出

```json
{
  "status": "failed",
  "error": {
    "code": "GENERATION_FAILED",
    "message": "无法生成内容：输入数据不足",
    "details": {
      "min_required_items": 5,
      "actual_items": 2
    }
  },
  "suggestion": "提供更多输入数据"
}
```

### 5. 审核型

#### 成功输出

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

#### 失败输出

```json
{
  "status": "failed",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "数据验证失败",
    "details": {
      "field": "email",
      "error": "格式无效"
    }
  },
  "suggestion": "检查数据格式"
}
```

---

## 扩展字段

### metadata 字段

所有输出都可以包含 `metadata` 字段，用于记录元数据：

```json
{
  "status": "success",
  "data": {...},
  "summary": "...",
  "metadata": {
    "timestamp": "2025-01-22T10:00:00Z",
    "duration_ms": 1500,
    "version": "1.0.0",
    "custom_field": "自定义值"
  }
}
```

### custom_fields 字段

各子智能体类型可以添加自定义字段：

```json
{
  "status": "success",
  "data": {
    "standard_field": "标准字段",
    "custom_field_1": "自定义字段1",
    "custom_field_2": "自定义字段2"
  },
  "summary": "..."
}
```

---

## 子智能体响应格式

### 简短响应（推荐）

```
✅ 任务完成
```

```
❌ 任务失败：错误原因
```

### 详细响应（不推荐）

```
✅ 任务完成。处理了100条数据，发现了5个问题，修复了3个bug，耗时2.5秒...
```

**注意**：子智能体应该只返回简短状态，详细数据应该保存到文件中。

---

## 错误处理最佳实践

### 1. 明确的错误信息

```json
{
  "error": {
    "code": "INPUT_NOT_FOUND",
    "message": "输入文件不存在：/path/to/file.json"
  }
}
```

### 2. 有用的恢复建议

```json
{
  "error": {...},
  "suggestion": "检查文件路径是否正确，确保文件存在"
}
```

### 3. 详细的错误详情

```json
{
  "error": {
    "code": "PROCESSING_FAILED",
    "message": "无法处理数据",
    "details": {
      "field": "content",
      "index": 42,
      "reason": "字段缺失"
    }
  }
}
```

---

## 主智能体处理输出

### 1. 解析状态

```python
# 检查状态码
if output["status"] == "success":
    # 处理成功
    pass
elif output["status"] == "failed":
    # 处理失败
    error_code = output["error"]["code"]
    error_message = output["error"]["message"]
```

### 2. 收集数据

```python
# 从文件读取详细数据
if output["status"] == "success":
    data_file = "/path/to/output.json"
    with open(data_file) as f:
        detailed_data = json.load(f)
```

### 3. 记录错误

```python
# 记录失败信息
if output["status"] == "failed":
    error_log.append({
        "task": task_name,
        "error": output["error"],
        "suggestion": output.get("suggestion", "")
    })
```

---

## 示例：完整输出

### 成功示例

**文件内容**（`/tmp/task_output.json`）：
```json
{
  "status": "success",
  "data": {
    "processed_items": [
      {"original": "A", "processed": "A_processed"}
    ],
    "total_processed": 1
  },
  "summary": "成功处理 1 条数据",
  "metadata": {
    "timestamp": "2025-01-22T10:00:00Z",
    "duration_ms": 500
  }
}
```

**子智能体响应**：
```
✅ 内容处理完成
```

### 失败示例

**文件内容**（`/tmp/task_output.json`）：
```json
{
  "status": "failed",
  "error": {
    "code": "INPUT_NOT_FOUND",
    "message": "输入文件不存在：/path/to/file.json",
    "details": {
      "path": "/path/to/file.json"
    }
  },
  "suggestion": "检查文件路径是否正确"
}
```

**子智能体响应**：
```
❌ 内容处理失败：输入文件不存在
```
