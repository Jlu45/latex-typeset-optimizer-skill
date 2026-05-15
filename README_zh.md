# LaTeX 排版优化工具

> 正在演进为 **LaTeX 项目诊断与构建编排器**

一个多模式的 LaTeX 排版优化工具，支持单文件优化、Overleaf/LaTeX 项目优化、编译日志分析和只读审查报告。下一阶段的重点是将工具从安全修复工具升级为完整的诊断与构建编排系统，具备更强的项目图谱、标准化的诊断、可复现的编译环境，以及 CI/IDE 接入能力。

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

### 安全修复边界

**在 safe 级别自动应用:**
- 去除尾部空白字符
- 规范化连续空行（最多 2 行）
- 确保文件末尾有换行符
- 通过 latexindent 重新缩进环境
- 移除重复的包导入（相同选项）
- 在 `\ref`、`\cite`、`\autoref` 前添加不间断空格

**永不自动修复:**
- 数学表达式重写
- 文档类更改
- 宏包替换
- 参考文献后端更改
- 引擎更改
- 启用 shell escape
- 出版商模板结构修改
- 语义文本编辑

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

## 相关项目与借鉴

| 项目 | 星数 / 定位 | 可借鉴点 |
|------|-------------|----------|
| **Overleaf** | ~17.7k，开源在线协作 LaTeX 编辑器 | 项目级思路；沙箱编译是核心风险（社区版缺失） |
| **LaTeX Workshop** | ~12.1k，VS Code LaTeX 全功能扩展 | root 文件发现、构建 recipes、多文件依赖解析、自动构建、问题面板、可配置 formatter/linter |
| **VimTeX** | ~6.3k，Vim/Neovim LaTeX 工作流插件 | 透明可调试：显示实际执行命令和编译输出 |
| **Tectonic** | ~4.8k，现代化自包含 TeX/LaTeX 引擎 | 可复现构建：自动下载支持文件、bundle 技术、自动 TeX/BibTeX 循环 |
| **TexLab** | ~2k，LaTeX LSP | 诊断服务化：build-on-save、.fls 项目检测、ChkTeX on open/edit、诊断 allow/ignore 模式 |
| **latex-action** | ~1.4k，GitHub Action 编译 LaTeX | CI 能力：容器化 TeXLive、固定版本、Alpine/Debian、多引擎、自定义字体/包、pre/post 脚本 |
| **latexindent.pl** | ~1k，LaTeX 格式化器 | 已在用；可进一步利用 YAML 配置、文本换行、段落处理、正则替换 |
| **TeXtidote** | ~1k，LaTeX 拼写/语法/风格检查 | 内容层审查：未引用的图片、标题大小写、LanguageTool 集成映射回 LaTeX 源位置 |
| **tex-fmt** | ~802，Rust 高性能格式化器 | 性能与低配置：.tex/.bib/.cls/.sty，极快、少配置、命令行友好 |
| **arara** | ~414，基于文档内指令的 TeX 自动化工具 | 文档内构建指令：`% arara: pdflatex`，自定义规则 |

## 演进路线图

下一阶段将工具从安全修复优化器升级为 **LaTeX 项目诊断与构建编排器**。

### v0.2：稳定性优先

**P0：安全沙箱编译与 zip/path 防护**
- 解压 zip 时防止 Zip Slip、绝对路径、`..`、符号链接逃逸
- 默认禁用 shell escape；发现 `minted`/`gnuplottex` 时只报告，不自动开启
- 编译使用临时目录、只读源副本、资源限制、超时限制
- 禁止读取用户主目录、环境变量、SSH key 等敏感路径
- 对项目内可执行文件、Makefile、pre/post 脚本默认禁用，除非用户显式开启
- 报告中增加 `security-notes` 区块

**P0：项目图谱与 root 检测重构**
- 支持 magic comments：`% !TEX root`、`% !TEX program`、`% !LW recipe`、`% arara:`
- 解析 `\input`、`\include`、`\subfile`、`\import`、`\bibliography`、`\addbibresource`、`\graphicspath`
- 编译后读取 `.fls`，用真实输入/输出文件修正静态依赖图
- 输出 `project-graph.json`，标注 root、子文件、bib、图片、cls/sty、本地包、外部资源

**P0：统一诊断模型**
- 标准化诊断模型，包含 `source`、`rule`、`severity`、`file`、`line`、`column`、`message`、`suggestion`、`fixable`、`safe_fix`
- 输出：`issue-summary.json`、`diagnostics.json`、`report.md`、`sarif.json`（GitHub Code Scanning）、可选 `annotations.md`（PR 评论）

**P1：双格式化后端**
- 默认：`latexindent`（兼容性好、YAML 可调）
- 快速模式：`tex-fmt`（适合大项目或 CI）
- 只格式化变更文件，避免全项目 diff 过大
- 幂等性检查：格式化两次 diff 应为空
- 跳过 `minted`、`lstlisting`、`verbatim`、自定义 verbatim 环境
- 输出"格式化风险提示"：修改行数、是否触及数学环境、是否触及模板文件

**P1：配置文件**
- `.latex-optimizer.yaml` 用于项目级设置

### v0.3：生态接入

**P1：构建 Recipes 系统**
- 支持可配置的构建 recipes（类似 LaTeX Workshop）：
  ```yaml
  recipes:
    default: latexmk-pdf
    latexmk-pdf:
      tools:
        - latexmk -pdf -file-line-error -halt-on-error -interaction=nonstopmode
    pdflatex-bibtex:
      tools:
        - pdflatex
        - bibtex
        - pdflatex
        - pdflatex
  ```
- 自动检测：`.latexmkrc`、`latexmkrc`、arara 指令、biber/bibtex、makeindex/xindy、glossaries
- 报告 `minted` 需要 shell escape，但不自动开启

**P1：Docker / 固定 TeXLive / Tectonic**
- 三种构建环境：

| 模式 | 适用场景 |
|------|----------|
| `local` | 用户本机已有 TeXLive/MiKTeX |
| `docker` | CI、投稿复现、隔离编译 |
| `tectonic` | 快速、可复现、自动拉取依赖的单文档构建 |

- 支持 `--texlive-version 2024/2025/2026/latest`
- 支持 `--docker-image`
- 编译前记录 `pdflatex --version`、`latexmk --version`、`biber --version`
- 输出 `environment.json`
- 缓存 TeXLive/Tectonic bundle
- 保留 `compile-before.log` / `compile-after.log`

**P1：CI / Pre-commit / GitHub Action 模板**
- `.github/workflows/latex-optimizer.yml`
- `.pre-commit-hooks.yaml`
- `latex-optimizer-action`
- PR 评论模板
- SARIF 上传示例
- Artifact 上传：PDF、报告、diff、issue-summary

### v0.4：智能审查

**P2：内容级诊断**
- 未引用的 figure/table/listing
- 重复 label
- 未定义 label/citation
- 未使用 bib entries
- 标题大小写检查
- 拼写/语法检查（TeXtidote / LanguageTool 集成）
- 中英文标点与空格检查
- CJK 文档引擎/字体建议
- 摘要、关键词、参考文献、附录结构检查

**P2：高级报告**
- HTML 报告生成
- PR review 注释
- 回归测试语料：Overleaf zip、arXiv 源码、CJK 论文、出版商模板
- 格式化幂等性与误改测试

### 最推荐先做的 5 个改动

| 优先级 | 改动 | 理由 |
|--------|------|------|
| **P0** | 安全沙箱 + zip/path 防护 | 项目模式的底线，尤其是处理用户上传 zip |
| **P0** | 项目图谱 + root 检测重构 | 直接提升复杂 Overleaf 项目成功率 |
| **P0** | 统一 diagnostics.json / SARIF | 让报告、CI、IDE、PR 评论都能复用同一套结果 |
| **P1** | Recipes 构建系统 | 支持 latexmk、pdflatex→bibtex→pdflatex、biber、makeindex、arara |
| **P1** | Docker/Tectonic 可复现构建 | 解决"我这里能编译、你那里不能编译"的 LaTeX 经典问题 |

## 安装

### 步骤 1: 克隆仓库

```bash
git clone https://github.com/Jlu45/latex-typeset-optimizer.git
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

## 许可证

本项目采用 MIT 许可证开源。

---

**English Version**: [README.md](README.md)