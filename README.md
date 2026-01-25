# waibuzheng 的 Skills 集合库

> **最后更新**：2026-01-25

## 🎯 这个项目干什么的？

这是一个 **Claude Code Skills 集合库**，每个 skill 都是独立的功能模块，可以直接拿来用。

**简单说**：
- ✅ 每个技能都能独立使用
- ✅ 遵循 skill-creator 最佳实践
- ✅ 想用哪个用哪个，灵活组合

## ✨ 现在能用的 Skills

| Skill | 功能 | 语言 | 状态 | 文档 |
|-------|------|------|------|------|
| [weekly-report-generator](./.claude/skills/weekly-report-generator/) | 从 Git 提交记录自动生成周报，支持 Word 模板和批量生成 | Python | ✅ 已实现 | [查看](./.claude/skills/weekly-report-generator/SKILL.md) |
## 🚀 快速上手

### 1. 安装 Skill


```bash
# 以周报生成器为例
npx skills add https://github.com/782042369/waibuzheng-skills/.claude/skills/weekly-report-generator --skill weekly-report-generator
```

### 2. 使用 Skill

启动 Claude Code，直接输入 skill 名称：

```bash
weekly-report-generator
 按提示提供参数：
  - 项目路径：`仓库1,仓库2`（多个项目用逗号分隔，单个项目直接写路径）
  - 时间范围：`本周`、`上周`、`本月`、`上月`、`本年`、`去年`，或具体日期如 `2026-01-01` 或 `2026-01-01-2026-01-07`
  - 命名规则：`xx第一周周报`、`xxx第二周周报`
  - 模板路径：Word 模板的绝对路径，如 `/path/to/report.docx`
  - 输出路径：结果保存的绝对路径，如 `/path/to/results`
---

---

## 📚 项目结构

```
waibuzheng-skills/
├── .claude/
│   └── skills/                      # Skills 集合
│       └── weekly-report-generator/ # 周报生成器
├── CLAUDE.md                        # AI 上下文文档
└── README.md                        # 本文件
```

**每个 Skill 的标准结构**：
```
.claude/skills/your-skill/
├── SKILL.md           # 核心文档（必需）
├── scripts/           # 脚本代码（如需要）
├── references/        # 参考文档（可选）
└── requirements.txt   # 依赖清单（Python 项目）
```

---

## 🔧 想添加新 Skill？

### 方法1：用 skill-creator 插件

```bash
npx skills add https://github.com/anthropics/skills/tree/main/skills/skill-creator --skill skill-creator
```

然后在 Claude Code 里输入：
```
根据 skill-creator 实现一个 xxx skill
```

---

## 📖 文档导航

- **[项目总体说明](./CLAUDE.md)** - 架构总览、模块索引、编码规范
- **[周报生成器文档](./.claude/skills/weekly-report-generator/SKILL.md)** - 使用指南和 API 参考

---

## 🛠️ 技术栈

- **Python Skills**：Python 3.8+、Git
- **Node.js Skills**：Node.js 20+、npm
- **文档**：Markdown、Mermaid

---

## 📊 项目状态

- **版本**：1.0.0
- **Skills 数量**：1
- **文档完整度**：100%

---

## 📄 License

MIT License

---

**有问题？** [提 Issue](https://github.com/782042369/waibuzheng-skills/issues)

_基于 [skill-creator](https://github.com/anthropics/skills) 最佳实践_
