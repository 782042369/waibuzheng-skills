# Weekly Report Generator

自动化生成专业周报文档，从 Git 提交记录转换为面向领导的工作汇报。

## ✨ 特性

- 📅 **灵活时间解析**：支持"本周"、"上周"、"2025.1.10-2025.1.15"等
- 🧠 **智能内容清洗**：将技术术语转换为业务语言
- 📊 **两种输出方式**：按天分类（周一到周五）或合并输出（凝练任务）
- 🔄 **多项目支持**：汇总多个项目的提交记录
- 🎨 **自定义风格**：基于用户提供的示例周报模仿生成
- 📝 **多格式输出**：支持 Markdown (.md) 和 Word (.docx)

## 🚀 快速开始

### 安装

```bash
pip install -r requirements.txt
```

### 使用

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

## 📖 文档

- [详细使用指南](./SKILL.md) - 完整的功能说明和使用场景
- [实现细节](./CLAUDE.md) - 架构设计和 API 文档
- [使用示例](./examples/) - 常见场景的完整示例

## 🛠️ 开发

### 运行测试

```bash
# 安装开发依赖
make install-dev

# 运行测试
make test

# 代码质量检查
make lint

# 格式化代码
make format
```

### 可用命令

```bash
make help           # 显示所有可用命令
make install        # 安装生产依赖
make install-dev    # 安装开发依赖
make test           # 运行测试（含覆盖率）
make test-quick     # 快速运行测试（无覆盖率）
make lint           # 代码质量检查
make format         # 格式化代码
make clean          # 清理临时文件
```

## 📂 项目结构

```
weekly-report-generator/
├── SKILL.md                 # 核心文档
├── CLAUDE.md                # 实现细节
├── README.md                # 本文件
├── requirements.txt         # 生产依赖
├── requirements-dev.txt     # 开发依赖
├── Makefile                 # 开发命令
├── scripts/                 # 核心脚本
│   ├── get_git_logs.py      # Git 日志获取
│   ├── export_report.py     # 周报导出
│   └── analyze_template.py  # 模板分析
├── references/              # 参考文档
│   └── report-prompts.md    # 内容清洗规则
├── examples/                # 使用示例
│   ├── basic-usage.md
│   ├── multi-project-demo.md
│   ├── style-matching-demo.md
│   └── sample-reports/      # 示例周报
└── tests/                   # 测试文件
    ├── test_git_logs.py
    └── test_export_report.py
```

## 🎯 使用场景

1. **从 Git 历史生成周报** - 自动提取提交记录
2. **转换为领导汇报风格** - 技术术语 → 业务语言
3. **多项目汇总周报** - 合并多个项目的工作内容
4. **基于示例定制格式** - 严格模仿你的周报风格

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

本 Skill 基于 [skill-creator](https://github.com/anthropics/skills) 最佳实践开发。
