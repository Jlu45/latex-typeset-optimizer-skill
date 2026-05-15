<div align="center">

# LaTeX Typeset Optimizer

> Evolving into a **LaTeX Project Diagnostic & Build Orchestrator**

[![Language](https://img.shields.io/badge/language-English%20%7C%20%E4%B8%AD%E6%96%87-blue)](README.md)

</div>

---

## 🌐 Language / 语言选择

| English | 简体中文 |
|---------|----------|
| [Read in English](#features) | [阅读中文版](#功能特性) |

---

---

## Features

A multi-mode LaTeX typeset optimization tool that supports single file optimization, Overleaf/LaTeX project optimization, compilation log analysis, and read-only review reports. The next phase focuses on upgrading from a safe-fix tool to a full diagnostic and build orchestration system with stronger project graphs, standardized diagnostics, reproducible compilation environments, and CI/IDE integration.

### Core Capabilities
- **Multi-mode Support**: Single file, project, review-only, and log analysis modes
- **Auto Mode Detection**: Automatically detects input type and selects appropriate mode
- **Formatting**: Uses latexindent for consistent LaTeX formatting
- **Linting**: Integrates chktex for code quality checking
- **Compilation**: Supports pdflatex, xelatex, and lualatex engines
- **Log Analysis**: Parses compilation logs to identify errors, warnings, and bad boxes
- **Safe Fixes**: Automatically applies safe fixes (whitespace, blank lines, nobreak spaces)
- **Diff Generation**: Creates unified diffs between original and optimized files
- **Report Generation**: Generates comprehensive Markdown reports and JSON issue summaries

### Service Modes

| Mode | User Scenario | Modifies Files | Output Artifacts |
|------|--------------|----------------|------------------|
| **Single File** | Single `.tex` file or pasted LaTeX | Generates optimized copy, never overwrites original | `optimized.tex`, `patch.diff`, `report.md` |
| **Project** | Overleaf project zip | Modifies in working copy | `optimized-project.zip`, `patch.diff`, `report.md`, `issue-summary.json` |
| **Review Only** | User says "just check" / "don't modify" | No file modifications | `report.md`, `issue-summary.json` |

### Evolution Roadmap

The next phase upgrades this tool into a **LaTeX Project Diagnostic & Build Orchestrator**:

- **v0.2**: Stability First - Security sandbox, project graph, unified diagnostics, build recipes, Docker/Tectonic support
- **v0.3**: Ecosystem Integration - GitHub Action, pre-commit hooks, CI templates
- **v0.4**: Intelligent Review - Content-level diagnostics, HTML reports, PR annotations

### Installation

```bash
# Clone the repository
git clone https://github.com/Jlu45/latex-typeset-optimizer.git
cd latex-typeset-optimizer

# Install dependencies
pip install -r requirements.txt
```

### Usage

```bash
# Single file optimization
python scripts/latex_optimizer.py --input paper.tex --mode single

# Project optimization (Overleaf zip)
python scripts/latex_optimizer.py --input project.zip --mode project

# Review-only mode
python scripts/latex_optimizer.py --input draft.tex --mode review

# With build environment
python scripts/latex_optimizer.py --input paper.tex --build-env docker
python scripts/latex_optimizer.py --input paper.tex --build-env tectonic
```

### License

This project is open source and available under the MIT License.

---

**[⬆️ Back to top / 返回顶部](#latex-typeset-optimizer)** | **[简体中文版本 / Chinese Version](#功能特性)**

---

---

## 功能特性

一个多模式的 LaTeX 排版优化工具，支持单文件优化、Overleaf/LaTeX 项目优化、编译日志分析和只读审查报告。下一阶段的重点是将工具从安全修复工具升级为完整的诊断与构建编排系统，具备更强的项目图谱、标准化的诊断、可复现的编译环境，以及 CI/IDE 接入能力。

### 核心能力
- **多模式支持**: 单文件、项目、仅审查和日志分析模式
- **自动模式检测**: 自动检测输入类型并选择合适的模式
- **格式化**: 使用 latexindent 实现一致的 LaTeX 格式
- **代码检查**: 集成 chktex 进行代码质量检查
- **编译支持**: 支持 pdflatex、xelatex 和 lualatex 引擎
- **日志分析**: 解析编译日志，识别错误、警告和坏盒子
- **安全修复**: 自动应用安全修复（空白字符、空行、不间断空格）
- **差异生成**: 创建原始文件和优化文件之间的统一差异
- **报告生成**: 生成全面的 Markdown 报告和 JSON 问题摘要

### 服务模式

| 模式 | 用户场景 | 修改文件 | 输出产物 |
|------|----------|----------|----------|
| **单文件** | 单个 `.tex` 文件或粘贴的 LaTeX 代码 | 生成优化副本，永不覆盖原文件 | `optimized.tex`, `patch.diff`, `report.md` |
| **项目** | Overleaf 项目压缩包 | 在工作副本中修改 | `optimized-project.zip`, `patch.diff`, `report.md`, `issue-summary.json` |
| **仅审查** | 用户要求"只检查" / "不要修改" | 不修改任何文件 | `report.md`, `issue-summary.json` |

### 演进路线图

下一阶段将工具升级为 **LaTeX 项目诊断与构建编排器**：

- **v0.2**: 稳定性优先 - 安全沙箱、项目图谱、统一诊断、构建 recipes、Docker/Tectonic 支持
- **v0.3**: 生态接入 - GitHub Action、pre-commit hooks、CI 模板
- **v0.4**: 智能审查 - 内容级诊断、HTML 报告、PR 注释

### 安装

```bash
# 克隆仓库
git clone https://github.com/Jlu45/latex-typeset-optimizer.git
cd latex-typeset-optimizer

# 安装依赖
pip install -r requirements.txt
```

### 使用方法

```bash
# 单文件优化
python scripts/latex_optimizer.py --input paper.tex --mode single

# 项目优化（Overleaf 压缩包）
python scripts/latex_optimizer.py --input project.zip --mode project

# 仅审查模式
python scripts/latex_optimizer.py --input draft.tex --mode review

# 使用构建环境
python scripts/latex_optimizer.py --input paper.tex --build-env docker
python scripts/latex_optimizer.py --input paper.tex --build-env tectonic
```

### 许可证

本项目采用 MIT 许可证开源。

---

**[⬆️ 返回顶部 / Back to top](#latex-typeset-optimizer)** | **[English Version / 英文版](#features)**