# LaTeX 排版优化工具

一个多模式的 LaTeX 排版优化工具，支持单文件优化、Overleaf/LaTeX 项目优化、编译日志分析和只读审查报告。

## 功能特性

- **多模式支持**: 单文件、项目、仅审查和日志分析模式
- **自动模式检测**: 自动检测输入类型并选择合适的模式
- **格式化**: 使用 latexindent 实现一致的 LaTeX 格式
- **代码检查**: 集成 chktex 进行代码质量检查
- **编译支持**: 支持 pdflatex、xelatex 和 lualatex 引擎
- **日志分析**: 解析编译日志，识别错误、警告和坏盒子
- **安全修复**: 自动应用安全修复（空白字符、空行、不间断空格）
- **差异生成**: 创建原始文件和优化文件之间的统一差异
- **报告生成**: 生成全面的 Markdown 报告和 JSON 问题摘要

## 服务模式

| 模式 | 用户场景 | 修改文件 | 输出产物 |
|------|----------|----------|----------|
| **单文件** | 单个 `.tex` 文件或粘贴的 LaTeX 代码 | 生成优化副本，永不覆盖原文件 | `optimized.tex`, `patch.diff`, `report.md` |
| **项目** | Overleaf 项目压缩包 | 在工作副本中修改 | `optimized-project.zip`, `patch.diff`, `report.md`, `issue-summary.json` |
| **仅审查** | 用户要求"只检查" / "不要修改" | 不修改任何文件 | `report.md`, `issue-summary.json` |

## 安装

### 步骤 1: 克隆仓库

```bash
git clone https://github.com/your-username/latex-typeset-optimizer.git
cd latex-typeset-optimizer
```

### 步骤 2: 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 步骤 3: 安装 LaTeX 发行版

LaTeX Typeset Optimizer 需要安装 LaTeX 发行版：

#### 选项 A: TeX Live（推荐 Linux/macOS 使用）

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install texlive-full latexmk latexindent chktex
```

**macOS (Homebrew):**
```bash
brew install texlive
brew install latexindent
brew install chktex
```

#### 选项 B: MiKTeX（推荐 Windows 使用）

1. 从 [miktex.org](https://miktex.org/) 下载并安装 MiKTeX
2. 安装过程中选择 "Install missing packages on-the-fly"
3. 打开 MiKTeX Console 并安装以下包：
   - `latexmk`
   - `latexindent`
   - `chktex`

### 步骤 4: 安装可选工具

#### latexindent（用于格式化）

```bash
# Ubuntu/Debian
sudo apt-get install latexindent

# macOS
brew install latexindent

# Windows（通过 MiKTeX Console）
# 搜索并安装 'latexindent' 包
```

#### chktex（用于代码检查）

```bash
# Ubuntu/Debian
sudo apt-get install chktex

# macOS
brew install chktex

# Windows（通过 MiKTeX Console）
# 搜索并安装 'chktex' 包
```

### 步骤 5: 验证安装

```bash
# 检查 Python 依赖
python -c "from scripts.latex_optimizer import main; print('Python dependencies OK')"

# 检查 LaTeX 安装
pdflatex --version
latexmk --version

# 检查可选工具（如果已安装）
latexindent --version 2>/dev/null || echo "latexindent not installed"
chktex --version 2>/dev/null || echo "chktex not installed"
```

### 系统要求

- Python 3.8+
- TeX Live (2020+) 或 MiKTeX (21.0+)
- latexmk（大多数 LaTeX 发行版已包含）
- latexindent（可选，推荐用于格式化）
- chktex（可选，推荐用于代码检查）

## 使用方法

```bash
# 单文件优化
python scripts/latex_optimizer.py --input paper.tex --mode single

# 项目优化（Overleaf 压缩包）
python scripts/latex_optimizer.py --input project.zip --mode project

# 仅审查模式
python scripts/latex_optimizer.py --input draft.tex --mode review

# 日志文件分析
python scripts/latex_optimizer.py --input compile.log --mode log-review

# 使用自定义选项
python scripts/latex_optimizer.py --input paper.tex --fix-level safe --compile-policy try
python scripts/latex_optimizer.py --input thesis.zip --engine xelatex --verbose
```

## 命令行选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--input` | 输入路径（.tex / .zip / .log / 目录） | 必填 |
| `--mode` | 运行模式：auto, single, project, review, log-review | auto |
| `--output` | 输出目录 | ./output |
| `--fix-level` | 修复级别：none, safe, suggest, aggressive | safe |
| `--compile-policy` | 编译策略：skip, try, required | try |
| `--write-policy` | 写入策略：report-only, copy, patch-only | copy |
| `--engine` | 强制指定引擎：pdflatex, xelatex, lualatex | 自动检测 |
| `--verbose` | 详细输出 | false |

## 问题严重性分类

| 类别 | 严重性 | 描述 |
|------|--------|------|
| compile-error | BLOCKING | 编译错误 |
| undefined-control-sequence | BLOCKING | 未定义的控制序列 |
| missing-package | HIGH | 缺失的包 |
| undefined-reference | HIGH | 未定义的引用 |
| undefined-citation | HIGH | 未定义的引用文献 |
| overfull-box | MEDIUM | 溢出盒子 |
| underfull-box | LOW | 内容不足盒子 |
| spacing-issue | LOW | 间距问题 |
| style-issue | INFO | 样式问题 |

## 安全修复（在 safe 级别自动应用）

- 去除尾部空白字符
- 规范化连续空行（最多 2 行）
- 确保文件末尾有换行符
- 通过 latexindent 重新缩进环境
- 移除重复的包导入（相同选项）
- 在 `\ref`、`\cite`、`\autoref` 前添加不间断空格

## 项目结构

```
latex-typeset-optimizer/
├── scripts/           # 主要 Python 脚本
├── configs/          # 配置文件
├── references/       # 文档资料
├── tests/            # 测试数据
└── agents/           # 代理配置
```

## 许可证

本项目采用 MIT 许可证开源。

---

**English Version**: [README.md](README.md)