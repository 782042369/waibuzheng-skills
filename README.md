# waibuzheng 的 Skills 集合库

> 最后更新：2026-01-20 18:00:00

## 📖 项目简介

这是一个用于存放多个技能（skills）的集合仓库，每个 skill 都是一个独立的功能模块，可以被外部系统调用和复用。

**核心理念**：
- 每个 skill 都是独立的、可复用的功能单元
- 遵循 skill-creator 最佳实践
- 支持灵活的组合和扩展

**项目特点**：
- 📦 Monorepo 架构，统一管理多个 skills
- 🤖 AI 友好，提供完整的上下文文档
- 🔧 可复用、可组合、可扩展
- 📝 标准化的文档结构和代码规范

## ✨ 当前包含的 Skills

| Skill | 描述 | 语言 | 状态 | 文档 |
|-------|------|------|------|------|
| [weekly-report-generator](./skills/weekly-report-generator/) | 自动化周报生成器，从 Git 提交记录生成专业工作汇报 | Python | ✅ 已实现 | [查看](./skills/weekly-report-generator/SKILL.md) |

## 🚀 快速开始

### 前置要求

- Python 3.8+ （使用 Python 的 skill）
- Node.js 20+ （使用 Node.js 的 skill）
- Git （部分 skill 需要）

### 安装和使用

1. **克隆仓库**
```bash
git clone <repository-url>
cd waibuzheng-skills
```

2. **安装特定 skill 的依赖**
```bash
# 例如：安装周报生成器的依赖
cd skills/weekly-report-generator
pip install -r requirements.txt
```

3. **使用 skill**
- 参考 skill 的 `SKILL.md` 文档
- 按照工作流程使用

**示例 - 周报生成器**：
```bash
# 1. 获取 Git 日志
python scripts/get_git_logs.py \
  --paths "/path/to/project" \
  --since "2025-01-13" \
  --until "2025-01-17"

# 2. AI 清洗内容（基于 references/report-prompts.md）

# 3. 导出周报
python scripts/export_report.py \
  --content "清洗后的内容" \
  --output "./output" \
  --filename "周报.md"
```

## 📚 如何添加新的 Skill

### 🚀 方法1：直接对话（最简单）⭐

**只需告诉 Claude 你想要什么**：

```
请帮我创建一个 skill，功能是：
[描述你想要的功能]

使用 Python，命名为 my-awesome-skill
```

**Claude 会自动**：
1. 创建完整的目录结构
2. 生成 SKILL.md 和 CLAUDE.md
3. 编写核心脚本
4. 更新项目文档

---

### 🔧 方法2：使用 skill-creator 插件

如果你想使用插件辅助：

```bash
# 1. 安装插件
# 使用 Claude Code 内置 skill
/plugin marketplace add anthropics/skills

# 2. 在对话中输入
根据 example-skills 中的 skill-creator 实现一个 xxx skill
```

---

### 📁 Skill 目录结构

Claude 创建的 skill 会遵循标准结构：

```
skills/your-skill-name/
├── SKILL.md                      # 核心文档（必需）
├── CLAUDE.md                     # AI 上下文（必需）
├── README.md                     # 使用说明（推荐）
├── requirements.txt              # Python 依赖
├── scripts/                      # 核心脚本
├── /                       # 资源文件（可选）
│   └── templates/
└── references/                   # 参考文档（可选）
```

**最小结构**：
```
skills/your-skill-name/
└── SKILL.md                      # 核心文档（必需）
```

## 📖 文档导航

### 项目级文档

- **[项目总体说明](./CLAUDE.md)** - AI 上下文文档，包含：
  - 项目愿景和架构总览
  - 模块结构图（Mermaid）
  - 模块索引和快速导航
  - 如何添加新的 Skill
  - 编码规范和 AI 使用指引

### Skill 级文档

- **[周报生成器 - 核心文档](./skills/weekly-report-generator/SKILL.md)** - 功能说明和使用流程
- **[周报生成器 - 实现细节](./skills/weekly-report-generator/CLAUDE.md)** - 架构设计和 API 文档
- **[周报生成器 - 快速开始](./skills/weekly-report-generator/README.md)** - 安装和基本用法

## 🎯 项目架构

```
waibuzheng-skills/
├── CLAUDE.md                    # 根级 AI 上下文
├── README.md                    # 根级说明（本文件）
├── .claude/
│   └── index.json               # 项目索引配置
└── skills/                      # Skills 集合
    ├── weekly-report-generator/
    │   ├── SKILL.md            # 核心 instructions
    │   ├── CLAUDE.md           # AI 上下文
    │   ├── README.md           # 使用说明
    │   ├── requirements.txt    # 依赖清单
    │   ├── scripts/            # 核心脚本（7个）
    │   │   ├── parse_time.py           # 智能时间解析 ⭐ 新增
    │   │   ├── get_git_logs.py         # 获取 Git 日志
    │   │   ├── export_report.py        # 导出 Markdown 周报
    │   │   ├── fill_template.py        # 填充 Word 模板
    │   │   ├── analyze_template.py     # 解析模板结构
    │   │   ├── calculate_weeks.py      # 计算周数（已废弃）
    │   │   └── update_task_status.py   # 更新任务状态
    │   └── references/         # 参考文档
    │       ├── script-api-reference.md  # 脚本 API 参考手册
    │       ├── subtask-workflow.md      # 子任务工作流程
    │       └── report-prompts.md        # 内容清洗规范
    └── [future skills...]
```

## 🤝 贡献指南

欢迎贡献新的 skills！请遵循以下规范：

1. **遵循 Skill 目录结构规范**
2. **创建完整的 SKILL.md 和 CLAUDE.md**
3. **添加必要的依赖文件**（如 requirements.txt）
4. **更新根级文档**（README.md 和 CLAUDE.md）
5. **遵循编码规范**（见 CLAUDE.md）

### 贡献流程

1. Fork 本仓库
2. 创建你的 skill 分支：`git checkout -b skill/my-new-skill`
3. 按照 Skill 标准创建目录和文件
4. 提交你的改动：`git commit -m "✨ feat: add my-new-skill"`
5. 推送到分支：`git push origin skill/my-new-skill`
6. 创建 Pull Request

## 📊 项目状态

- **版本**：1.0.0
- **最后更新**：2026-01-20
- **Skills 数量**：1
- **文档覆盖率**：100%
- **测试覆盖率**：待完善

## 🛠️ 技术栈

- **Python Skills**：Python 3.8+、Git
- **Node.js Skills**：Node.js 20+、npm
- **文档工具**：Markdown、Mermaid
- **版本控制**：Git

## 📝 变更记录

### 2026-01-20 - v1.0.0
- ✨ **重大更新**：新增 `parse_time.py` 智能时间解析脚本
  - 支持相对时间表达（本周/上周/本月/上月/本年/去年）
  - 支持绝对时间范围（YYYY-MM-DD-YYYY-MM-DD）
  - 支持单个日期并自动计算所在周（YYYY-MM-DD）
  - 按自然周（周一到周日）划分时间范围
  - Windows 环境友好，UTF-8 编码支持
- ♻️ **架构重构**：主子智能体职责分离
  - 主智能体：只做数据准备和验证，不创建文件
  - 子智能体：独立完成所有工作，创建临时文件和周报文件
- 📝 **文档完善**：
  - 重写 `SKILL.md`，明确主子智能体职责划分
  - 更新 `script-api-reference.md`，添加 parse_time.py API 文档
  - 更新项目架构图，标注新增脚本
- 🗑️ **废弃标记**：`calculate_weeks.py` 已废弃，推荐使用 `parse_time.py`

### 2026-01-16 - v3.0.0
- 🎉 项目初始化，创建 monorepo 结构
- ✨ 实现 `weekly-report-generator` skill
- 📝 编写完整的项目文档
- 🔧 配置 `.claude/index.json` 索引

## 📄 许可证

MIT License

## 📮 联系方式

- **项目维护者**：waibuzheng
- **问题反馈**：通过 GitHub Issues
- **功能建议**：通过 GitHub Discussions

---

**Happy Coding! 🎉**

_这个项目使用 [skill-creator](https://github.com/anthropics/skills) 最佳实践开发_
