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

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/latex-typeset-optimizer.git
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

## Issue Severity Classification

| Category | Severity | Description |
|----------|----------|-------------|
| compile-error | BLOCKING | Compilation errors |
| undefined-control-sequence | BLOCKING | Undefined control sequences |
| missing-package | HIGH | Missing packages |
| undefined-reference | HIGH | Undefined references |
| undefined-citation | HIGH | Undefined citations |
| overfull-box | MEDIUM | Overfull boxes |
| underfull-box | LOW | Underfull boxes |
| spacing-issue | LOW | Spacing issues |
| style-issue | INFO | Style issues |

## Safe Fixes (Auto-applied at safe level)

- Trim trailing whitespace
- Normalize consecutive blank lines (max 2)
- Ensure final newline
- Re-indent environments via latexindent
- Remove duplicate package imports (identical options)
- Add non-breaking spaces before `\ref`, `\cite`, `\autoref`

## Project Structure

```
latex-typeset-optimizer/
├── scripts/           # Main Python scripts
├── configs/          # Configuration files
├── references/       # Documentation
├── tests/            # Test fixtures
└── agents/           # Agent configurations
```

## License

This project is open source and available under the MIT License.

---

**简体中文版本**: [README_zh.md](README_zh.md)