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

## 技术架构

### 系统概览

LaTeX Typeset Optimizer 采用模块化的流水线架构，将 LaTeX 文件通过多个阶段处理：

```
┌─────────────────────────────────────────────────────────────────┐
│                      输入层                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  .tex 文件  │  │  .zip (OL)  │  │  .log 文件  │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      模式路由器                                  │
│    自动检测输入类型 → 选择处理模式                                │
└──────────────────────────────┬──────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
    ┌───────────┐       ┌───────────┐       ┌───────────┐
    │  单文件   │       │   项目    │       │  日志分析 │
    │           │       │           │       │           │
    └─────┬─────┘       └─────┬─────┘       └─────┬─────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     处理流水线                                   │
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ 输入处理 │ →  │ 项目检测 │ →  │ 格式化   │ →  │ 代码检查 │  │
│  │          │    │          │    │          │    │          │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│         ↓                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ 编译     │ →  │ 日志解析 │ →  │ 问题分类 │ →  │ 安全修复 │  │
│  │          │    │          │    │          │    │          │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      输出层                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ 优化后的   │  │ report.md   │  │ patch.diff  │             │
│  │ .tex/.zip  │  │             │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

### 核心组件

| 组件 | 描述 | 主要职责 |
|------|------|----------|
| **IntakeProcessor** | 输入处理 | 接受 .tex、.zip、.log 或目录输入 |
| **ProjectDetector** | 项目分析 | 识别 main.tex、引擎类型、包依赖 |
| **ToolManager** | 工具选择 | 根据项目需求选择合适的工具 |
| **TexFormatter** | 代码格式化 | 应用 latexindent 格式化规则 |
| **TexLinter** | 代码质量检查 | 运行 chktex/lacheck 进行检查 |
| **TexCompiler** | 编译 | 使用检测到的引擎执行 latexmk |
| **LogParser** | 日志分析 | 解析编译日志中的错误/警告 |
| **IssueClassifier** | 问题分类 | 按严重性和类别分类问题 |
| **SafeFixer** | 自动修复 | 应用安全修复（空白字符、格式化） |
| **DiffGenerator** | 差异生成 | 创建原始文件和优化文件之间的差异 |
| **ReportGenerator** | 报告生成 | 生成 Markdown 报告和 JSON 摘要 |
| **OutputPackager** | 输出打包 | 将项目打包为 zip 文件 |

### 脚本结构

```
scripts/
├── latex_optimizer.py    # 主入口，协调工作流程
├── intake.py             # 输入处理（解压、复制）
├── detect_project.py     # 项目结构检测
├── detect_main_tex.py    # 主 .tex 文件识别
├── tool_check.py         # 外部工具可用性检查
├── format_tex.py         # LaTeX 格式化（latexindent）
├── lint_tex.py           # 代码检查（chktex）
├── compile_tex.py        # 编译（latexmk）
├── parse_log.py          # 日志文件解析
├── classify_issues.py    # 问题分类
├── apply_safe_fixes.py   # 安全修复应用
├── diff_utils.py         # 差异生成
├── make_report.py        # 报告生成
├── package_output.py     # 输出打包
└── models.py             # 数据模型（Pydantic）
```

### 数据模型

**核心 Pydantic 模型:**
- `OptimizerConfig`: 配置选项（输入、模式、修复级别等）
- `ProjectInfo`: 项目元数据（main_tex、tex_files、引擎、包）
- `ToolSet`: 选定的外部工具（格式化器、引擎、检查器）
- `Issue`: 单个问题（严重性、类别、消息、建议）
- `IssueSummary`: 汇总问题（按严重性计数、所有问题）
- `FixResult`: 修复应用结果（已应用、失败、已修改）
- `OptimizationResult`: 完整结果（使用模式、项目信息、问题摘要、修复结果）

### 引擎检测逻辑

```
输入: .tex 文件头部
├─ %!TEX program = xelatex → 使用 xelatex
├─ %!TEX program = lualatex → 使用 lualatex
├─ %!TEX program = pdflatex → 使用 pdflatex
├─ ctex/xeCJK/luatexja/kotex → 使用 xelatex
├─ fontspec → 使用 xelatex 或 lualatex
├─ pstricks → 使用 xelatex 或 latex+dvips
└─ 默认 → 使用 pdflatex
```

### 问题严重性分类

| 严重性 | 定义 | 示例 |
|--------|------|------|
| **BLOCKING** | 阻止编译 | 未定义的控制序列、缺失的包 |
| **HIGH** | 严重问题 | 未定义的引用/引用文献 |
| **MEDIUM** | 可能影响输出质量 | 溢出盒子 |
| **LOW** | 次要问题 | 内容不足盒子、间距问题 |
| **INFO** | 样式建议 | 格式化改进 |

### 工作流程详情

#### 单文件模式
1. 将输入文件复制到临时工作区
2. 从头部检测引擎和包
3. 使用 latexindent 格式化
4. 使用 chktex 检查
5. 使用 latexmk 编译
6. 解析日志中的错误/警告
7. 按严重性分类问题
8. 应用安全修复
9. 生成差异和报告
10. 输出优化后的文件

#### 项目模式
1. 将 Overleaf 项目解压到工作区
2. 识别 main.tex 并构建依赖图
3. 格式化所有 .tex 文件
4. 检查所有 .tex 文件
5. 完整编译（含参考文献）
6. 解析编译日志
7. 分类所有问题
8. 对所有文件应用安全修复
9. 生成项目范围的差异
10. 打包为 optimized-project.zip

## 许可证

本项目采用 MIT 许可证开源。

---

**English Version**: [README.md](README.md)