# LaTeX Typeset Optimizer

A multi-mode LaTeX typeset optimization tool that supports single file optimization, Overleaf/LaTeX project optimization, compilation log analysis, and read-only review reports.

## Features

- **Multi-mode Support**: Single file, project, review-only, and log analysis modes
- **Auto Mode Detection**: Automatically detects input type and selects appropriate mode
- **Formatting**: Uses latexindent for consistent LaTeX formatting
- **Linting**: Integrates chktex for code quality checking
- **Compilation**: Supports pdflatex, xelatex, and lualatex engines
- **Log Analysis**: Parses compilation logs to identify errors, warnings, and bad boxes
- **Safe Fixes**: Automatically applies safe fixes (whitespace, blank lines, nobreak spaces)
- **Diff Generation**: Creates unified diffs between original and optimized files
- **Report Generation**: Generates comprehensive Markdown reports and JSON issue summaries

## Service Modes

| Mode | User Scenario | Modifies Files | Output Artifacts |
|------|--------------|----------------|------------------|
| **Single File** | Single `.tex` file or pasted LaTeX | Generates optimized copy, never overwrites original | `optimized.tex`, `patch.diff`, `report.md` |
| **Project** | Overleaf project zip | Modifies in working copy | `optimized-project.zip`, `patch.diff`, `report.md`, `issue-summary.json` |
| **Review Only** | User says "just check" / "don't modify" | No file modifications | `report.md`, `issue-summary.json` |

## Technical Architecture

### System Overview

The LaTeX Typeset Optimizer follows a modular, pipeline-based architecture that processes LaTeX files through multiple stages:

```
┌─────────────────────────────────────────────────────────────────┐
│                      INPUT LAYER                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  .tex File  │  │  .zip (OL)  │  │  .log File  │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MODE ROUTER                                │
│    Auto-detects input type → selects processing mode            │
└──────────────────────────────┬──────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
    ┌───────────┐       ┌───────────┐       ┌───────────┐
    │  SINGLE   │       │  PROJECT  │       │   LOG     │
    │   FILE    │       │           │       │  REVIEW   │
    └─────┬─────┘       └─────┬─────┘       └─────┬─────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PROCESSING PIPELINE                         │
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ Intake   │ →  │ Detect   │ →  │ Format   │ →  │ Lint     │  │
│  │          │    │          │    │          │    │          │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│         ↓                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ Compile  │ →  │ LogParse │ →  │ Classify │ →  │ Fix      │  │
│  │          │    │          │    │          │    │          │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OUTPUT LAYER                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ optimized   │  │ report.md   │  │ patch.diff  │             │
│  │ .tex/.zip   │  │             │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

| Component | Description | Key Responsibilities |
|-----------|-------------|---------------------|
| **IntakeProcessor** | Input handling | Accepts .tex, .zip, .log, or directory inputs |
| **ProjectDetector** | Project analysis | Identifies main.tex, engine type, package dependencies |
| **ToolManager** | Tool selection | Selects appropriate tools based on project requirements |
| **TexFormatter** | Code formatting | Applies latexindent formatting rules |
| **TexLinter** | Code quality | Runs chktex/lacheck for linting |
| **TexCompiler** | Compilation | Executes latexmk with detected engine |
| **LogParser** | Log analysis | Parses compilation logs for errors/warnings |
| **IssueClassifier** | Issue categorization | Classifies issues by severity and category |
| **SafeFixer** | Auto-fixes | Applies safe fixes (whitespace, formatting) |
| **DiffGenerator** | Diff generation | Creates unified diff between original and optimized |
| **ReportGenerator** | Report creation | Generates Markdown report and JSON summary |
| **OutputPackager** | Output packaging | Packages project as zip file |

### Scripts Structure

```
scripts/
├── latex_optimizer.py    # Main entry point, orchestrates workflow
├── intake.py             # Input processing (unzip, copy)
├── detect_project.py     # Project structure detection
├── detect_main_tex.py    # Main .tex file identification
├── tool_check.py         # External tool availability check
├── format_tex.py         # LaTeX formatting (latexindent)
├── lint_tex.py           # Linting (chktex)
├── compile_tex.py        # Compilation (latexmk)
├── parse_log.py          # Log file parsing
├── classify_issues.py    # Issue classification
├── apply_safe_fixes.py   # Safe fix application
├── diff_utils.py         # Diff generation
├── make_report.py        # Report generation
├── package_output.py     # Output packaging
└── models.py             # Data models (Pydantic)
```

### Data Models

**Key Pydantic Models:**
- `OptimizerConfig`: Configuration options (input, mode, fix_level, etc.)
- `ProjectInfo`: Project metadata (main_tex, tex_files, engine, packages)
- `ToolSet`: Selected external tools (formatter, engine, linters)
- `Issue`: Individual issue (severity, category, message, recommendation)
- `IssueSummary`: Aggregated issues (counts by severity, all issues)
- `FixResult`: Fix application results (applied, failed, modified)
- `OptimizationResult`: Complete result (mode_used, project_info, issue_summary, fix_result)

### Engine Detection Logic

```
Input: .tex file header
├─ %!TEX program = xelatex → use xelatex
├─ %!TEX program = lualatex → use lualatex
├─ %!TEX program = pdflatex → use pdflatex
├─ ctex/xeCJK/luatexja/kotex → use xelatex
├─ fontspec → use xelatex or lualatex
├─ pstricks → use xelatex or latex+dvips
└─ default → use pdflatex
```

### Issue Severity Classification

| Severity | Definition | Examples |
|----------|------------|----------|
| **BLOCKING** | Prevents compilation | Undefined control sequences, missing packages |
| **HIGH** | Critical issues | Undefined references/citations |
| **MEDIUM** | May affect output quality | Overfull boxes |
| **LOW** | Minor issues | Underfull boxes, spacing issues |
| **INFO** | Style suggestions | Formatting improvements |

### Workflow Details

#### Single File Mode
1. Copy input file to temporary workspace
2. Detect engine and packages from header
3. Format using latexindent
4. Lint using chktex
5. Compile with latexmk
6. Parse log for errors/warnings
7. Classify issues by severity
8. Apply safe fixes
9. Generate diff and report
10. Output optimized file

#### Project Mode
1. Unzip Overleaf project to workspace
2. Identify main.tex and build dependency graph
3. Format all .tex files
4. Lint all .tex files
5. Full compilation with bibliography
6. Parse compilation log
7. Classify all issues
8. Apply safe fixes to all files
9. Generate project-wide diff
10. Package as optimized-project.zip

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/Jlu45/latex-typeset-optimizer.git
cd latex-typeset-optimizer
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Install LaTeX Distribution

LaTeX Typeset Optimizer requires a LaTeX distribution to be installed:

#### Option A: TeX Live (Recommended for Linux/macOS)

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

#### Option B: MiKTeX (Recommended for Windows)

1. Download and install MiKTeX from [miktex.org](https://miktex.org/)
2. During installation, select "Install missing packages on-the-fly"
3. Open MiKTeX Console and install the following packages:
   - `latexmk`
   - `latexindent`
   - `chktex`

### Step 4: Install Optional Tools

#### latexindent (for formatting)

```bash
# Ubuntu/Debian
sudo apt-get install latexindent

# macOS
brew install latexindent

# Windows (via MiKTeX Console)
# Search for and install 'latexindent' package
```

#### chktex (for linting)

```bash
# Ubuntu/Debian
sudo apt-get install chktex

# macOS
brew install chktex

# Windows (via MiKTeX Console)
# Search for and install 'chktex' package
```

### Step 5: Verify Installation

```bash
# Check Python dependencies
python -c "from scripts.latex_optimizer import main; print('Python dependencies OK')"

# Check LaTeX installation
pdflatex --version
latexmk --version

# Check optional tools (if installed)
latexindent --version 2>/dev/null || echo "latexindent not installed"
chktex --version 2>/dev/null || echo "chktex not installed"
```

### System Requirements

- Python 3.8+
- TeX Live (2020+) or MiKTeX (21.0+)
- latexmk (included with most LaTeX distributions)
- latexindent (optional, recommended for formatting)
- chktex (optional, recommended for linting)

## Usage

```bash
# Single file optimization
python scripts/latex_optimizer.py --input paper.tex --mode single

# Project optimization (Overleaf zip)
python scripts/latex_optimizer.py --input project.zip --mode project

# Review-only mode
python scripts/latex_optimizer.py --input draft.tex --mode review

# Log file analysis
python scripts/latex_optimizer.py --input compile.log --mode log-review

# With custom options
python scripts/latex_optimizer.py --input paper.tex --fix-level safe --compile-policy try
python scripts/latex_optimizer.py --input thesis.zip --engine xelatex --verbose
```

## CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input` | Input path (.tex / .zip / .log / directory) | required |
| `--mode` | Run mode: auto, single, project, review, log-review | auto |
| `--output` | Output directory | ./output |
| `--fix-level` | Fix level: none, safe, suggest, aggressive | safe |
| `--compile-policy` | Compile policy: skip, try, required | try |
| `--write-policy` | Write policy: report-only, copy, patch-only | copy |
| `--engine` | Force specific engine: pdflatex, xelatex, lualatex | auto-detect |
| `--verbose` | Verbose output | false |

## Safe Fixes (Auto-applied at safe level)

- Trim trailing whitespace
- Normalize consecutive blank lines (max 2)
- Ensure final newline
- Re-indent environments via latexindent
- Remove duplicate package imports (identical options)
- Add non-breaking spaces before `\ref`, `\cite`, `\autoref`

## License

This project is open source and available under the MIT License.

---

**简体中文版本**: [README_zh.md](README_zh.md)