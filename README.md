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
| [weekly-report-generator](./.claude/skills/weekly-report-generator/) | 自动化周报生成器，从 Git 提交记录生成专业工作汇报 | Python | ✅ 已实现 | [查看](./.claude/skills/weekly-report-generator/SKILL.md) |

## 🚀 快速开始

### 前置要求

- Python 3.8+ （使用 Python 的 skill）
- Node.js 20+ （使用 Node.js 的 skill）
- Git （部分 skill 需要）

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/782042369/waibuzheng-skills.git
cd waibuzheng-skills
```

2. **复制 skill 到对应目录**

**不同 AI 工具的安装路径**：

| AI 工具 | 复制路径 |
| ------- | ------------------------------------------------ |
| Claude Code | `~/.claude/skills/` |
| Cursor | `.cursor/commands/` + `.shared/` |
| Windsurf | `.windsurf/workflows/` + `.shared/` |
| GitHub Copilot | `.github/prompts/` + `.shared/` |

**示例（Claude Code）**：
```bash
cp -r .claude/skills/weekly-report-generator ~/.claude/skills/
```

3. **启动 AI 助手并使用 skill**

以 `weekly-report-generator` 为例：

- 启动 Claude Code
- 输入：`weekly-report-generator`
- 按提示提供参数：
  - **项目路径**：`仓库1,仓库2`（多个项目用逗号分隔，单个项目直接写路径）
  - **时间范围**：`本周`、`上周`、`本月`、`上月`、`本年`、`去年`，或具体日期如 `2026-01-01` 或 `2026-01-01-2026-01-07`
  - **命名规则**：`xx第一周周报`、`xxx第二周周报`
  - **模板路径**：Word 模板的绝对路径，如 `/path/to/report.docx`
  - **输出路径**：结果保存的绝对路径，如 `/path/to/results`

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
└── templates/                   # 资源文件（可选）
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

- **[周报生成器 - 核心文档](./.claude/skills/weekly-report-generator/SKILL.md)** - 功能说明和使用流程

## 🎯 项目架构

```
waibuzheng-skills/
├── CLAUDE.md                    # 根级 AI 上下文
├── README.md                    # 根级说明（本文件）
├── .claude/
│   └── index.json               # 项目索引配置
│   └── skills/                      # Skills 集合
│       └── weekly-report-generator/
```

## 📊 项目状态

- **版本**：1.0.0
- **最后更新**：2026-01-20
- **Skills 数量**：1
- **文档覆盖率**：100%

## 🛠️ 技术栈

- **Python Skills**：Python 3.8+、Git
- **Node.js Skills**：Node.js 20+、npm
- **文档工具**：Markdown、Mermaid
- **版本控制**：Git

## 📄 许可证

MIT License

## 📮 联系方式

- **项目维护者**：waibuzheng
- **问题反馈**：通过 GitHub Issues
- **功能建议**：通过 GitHub Discussions

---

**Happy Coding! 🎉**

_这个项目使用 [skill-creator](https://github.com/anthropics/skills) 最佳实践开发_
