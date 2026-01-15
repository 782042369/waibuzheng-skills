# waibuzheng 的 Skills 集合库

> 最后更新：2026-01-15 22:15:00

## 📖 项目简介

这是一个用于存放多个技能（skills）的集合仓库，每个 skill 都是一个独立的功能模块，可以被外部系统调用和复用。

**核心理念**：
- 每个 skill 都是独立的、可复用的功能单元
- 遵循 skill-creator 最佳实践
- 支持灵活的组合和扩展

## ✨ 当前包含的 Skills

| Skill | 描述 | 语言 | 状态 |
|-------|------|------|------|
| [weekly-report-generator](./skills/weekly-report-generator/) | 自动化周报生成器，从Git提交记录生成专业工作汇报 | Python | ✅ 已实现 |

## 🚀 快速开始

### 前置要求

- Python 3.8+ （使用 Python 的 skill）
- Node.js 16+ （使用 Node.js 的 skill）
- Git （部分 skill 需要）

### 安装和使用

1. **克隆仓库**
```bash
git clone <repository-url>
cd weekly-report
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
/plugin marketplace add anthropics/skills

# 2. 在对话中输入
skill-creator create my-skill
```

---

### 📁 Skill 目录结构

Claude 创建的 skill 会遵循标准结构：

```
skills/your-skill-name/
├── SKILL.md                      # 核心文档（必需）
├── CLAUDE.md                     # AI 上下文（必需）
├── requirements.txt              # Python 依赖
├── scripts/                      # 核心脚本
├── assets/                       # 资源文件
│   └── templates/
└── references/                   # 参考文档
```

## 📖 文档导航

- [项目总体说明](./CLAUDE.md) - AI 上下文文档
- [Skills 规范](./CLAUDE.md#如何添加新的-skill) - 如何添加新的 skill
- [周报生成器文档](./skills/weekly-report-generator/) - 查看具体 skill 实现

## 🤝 贡献指南

欢迎贡献新的 skills！请遵循以下规范：

1. 遵循 Skill 目录结构规范
2. 创建完整的 SKILL.md 和 CLAUDE.md
3. 添加必要的依赖文件
4. 更新根级文档

## 📝 许可证

待定

## 📮 联系方式

- 项目维护者：waibuzheng
- 问题反馈：通过 GitHub Issues

---

**Happy Coding! 🎉**
