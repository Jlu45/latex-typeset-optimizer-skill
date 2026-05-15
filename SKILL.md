---
name: "latex-typeset-optimizer"
description: "LaTeX Project Diagnostic & Build Orchestrator: format, lint, compile, log-parse, safe-fix, project graph, build recipes, reproducible builds, SARIF diagnostics for .tex files and Overleaf projects. Invoke when optimizing LaTeX, fixing overfull boxes, checking compilation, reviewing .tex/.zip projects, or setting up LaTeX CI."
---

# LaTeX Typeset Optimizer

> LaTeX Project Diagnostic & Build Orchestrator

A multi-mode LaTeX typeset optimization tool evolving into a full diagnostic and build orchestration system with stronger project graphs, standardized diagnostics, reproducible compilation environments, and CI/IDE integration.

## Service Modes

| Mode | User Scenario | Modifies Files | Output Artifacts |
|------|--------------|----------------|------------------|
| **A. Single File** | Single `.tex` file or pasted LaTeX | Generates optimized copy, never overwrites original | `optimized.tex`, `patch.diff`, `report.md` |
| **B. Project** | Overleaf project zip | Modifies in working copy | `optimized-project.zip`, `patch.diff`, `report.md`, `issue-summary.json`, `diagnostics.json`, `sarif.json`, `project-graph.json`, `environment.json` |
| **C. Review Only** | User says "just check" / "don't modify" | No file modifications | `report.md`, `issue-summary.json`, `diagnostics.json`, `sarif.json` |

## When to Invoke

Invoke this skill when the user:
- Asks to optimize, format, or lint a LaTeX file
- Uploads a `.tex` file or Overleaf `.zip` project
- Wants to check for overfull/underfull boxes
- Needs compilation log analysis
- Asks for a review-only audit of LaTeX source
- Mentions LaTeX typesetting issues, bad boxes, undefined references
- Wants to set up LaTeX CI/CD pipelines
- Needs reproducible build environments (Docker/Tectonic)
- Wants SARIF output for GitHub Code Scanning
- Needs project dependency graph analysis

## Mode Routing Rules

The skill automatically detects the appropriate mode:

1. **Review-only triggers**: "只检查", "不要修改", "不要改文件", "只给报告", "review only", "audit only", "no edits", "no changes", "只审查", "仅检查", "不要动文件"
2. **Project triggers**: `.zip` input, "overleaf", "项目", "project", "论文", "thesis", "dissertation", "投稿", "submission", "arxiv"
3. **Log review**: `.log` file input
4. **Single file**: `.tex` file input (default)

## Workflow

### Single File Optimization

```
1. Intake: Copy .tex to temp workspace (with security sandbox)
2. Detect: Parse header, identify engine, packages, CJK usage, magic comments
3. Tool Check: Verify latexindent/tex-fmt/chktex availability
4. Config: Load .latex-optimizer.yaml if present
5. Environment: Detect build environment versions
6. Recipe: Select build recipe based on project analysis
7. Format: Apply latexindent or tex-fmt (with basic fallback)
8. Lint: Run chktex/lacheck if available
9. Compile: Execute recipe via latexmk/docker/tectonic
10. Parse Log: Extract errors, warnings, bad boxes, undefined refs
11. Classify: Categorize issues by severity (BLOCKING/HIGH/MEDIUM/LOW/INFO)
12. Diagnose: Generate unified diagnostics (Diagnostic model)
13. Safe Fix: Apply safe-level fixes (trailing whitespace, blank lines, nobreak spaces)
14. Generate Diff: Create unified diff between original and optimized
15. Report: Generate Markdown report + JSON issue summary + diagnostics.json + sarif.json
16. Output: optimized.tex, patch.diff, report.md, issue-summary.json, diagnostics.json, sarif.json, environment.json
```

### Project Optimization

```
1. Intake: Unzip to temp workspace (with Zip Slip/symlink protection)
2. Detect: Find main.tex, build project graph, detect engine/bib backend, magic comments, arara directives
3. Tool Check: Verify all required tools
4. Config: Load .latex-optimizer.yaml if present
5. Environment: Detect build environment versions
6. Recipe: Select build recipe based on project analysis
7. Format: Format all .tex files in project (with idempotency check)
8. Lint: Lint all .tex files
9. Compile: Full build with selected recipe (latexmk/docker/tectonic)
10. Parse Log: Parse compilation log
11. Read .fls: Update project graph with real I/O data
12. Classify: Classify all issues
13. Diagnose: Generate unified diagnostics
14. Safe Fix: Apply safe fixes to all files
15. Generate Diff: Project-wide diff
16. Report: Generate comprehensive report + all diagnostic outputs
17. Package: Re-zip as optimized-project.zip
18. Output: optimized-project.zip, patch.diff, report.md, issue-summary.json, diagnostics.json, sarif.json, project-graph.json, environment.json
```

### Review-Only Mode

```
1. Intake: Copy input to workspace (read-only, sandboxed)
2. Detect: Analyze project structure, build project graph
3. Compile: Try compilation to detect issues
4. Parse Log: Parse compilation log
5. Classify: Classify all issues
6. Diagnose: Generate unified diagnostics
7. Report: Generate detailed review report
8. Output: report.md, issue-summary.json, diagnostics.json, sarif.json (NO file modifications)
```

## Engine Selection Decision Tree

```
Input: tex file header
├─ %!TEX program = xelatex → use xelatex
├─ %!TEX program = lualatex → use lualatex
├─ %!TEX program = pdflatex → use pdflatex
├─ ctex/xeCJK/luatexja/kotex → use xelatex
├─ fontspec → use xelatex or lualatex
├─ pstricks → use xelatex or latex+dvips
└─ default → use pdflatex
```

## Magic Comment Support

```
% !TEX root = ../main.tex        → Follow to find root document
% !TEX program = xelatex         → Override engine selection
% !LW recipe = latexmk-xelatex   → Select build recipe
% arara: pdflatex                 → Arara build directive
```

## Build Recipes

| Recipe | Tools | Use Case |
|--------|-------|----------|
| `latexmk-pdf` | latexmk -pdf | Default PDF build |
| `latexmk-xelatex` | latexmk -pdf -pdflatex=xelatex | CJK / fontspec projects |
| `latexmk-lualatex` | latexmk -pdf -pdflatex=lualatex | LuaLaTeX projects |
| `pdflatex-bibtex` | pdflatex → bibtex → pdflatex → pdflatex | Manual bibtex workflow |
| `pdflatex-biber` | pdflatex → biber → pdflatex → pdflatex | BibLaTeX/biber workflow |
| `tectonic` | tectonic | Reproducible single-document build |

Auto-detection priority: arara directives → .latexmkrc → engine_hint → bib_backend → default

## Build Environments

| Environment | Use Case | CLI Flag |
|-------------|----------|----------|
| `local` | User's existing TeXLive/MiKTeX | `--build-env local` |
| `docker` | CI, submission reproduction, isolated compilation | `--build-env docker` |
| `tectonic` | Fast, reproducible, auto-pull dependencies | `--build-env tectonic` |

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
| security-note | INFO | Security warnings |

## Unified Diagnostic Model

```json
{
  "source": "chktex | latexmk | biber | textidote | safe-fixer",
  "rule": "ChkTeX-13",
  "severity": "BLOCKING | HIGH | MEDIUM | LOW | INFO",
  "file": "sections/intro.tex",
  "line": 42,
  "column": 13,
  "message": "...",
  "suggestion": "...",
  "fixable": true,
  "safe_fix": false
}
```

## Safe Fixes (Auto-applied at safe level)

- Trim trailing whitespace
- Normalize consecutive blank lines (max 2)
- Ensure final newline
- Re-indent environments via latexindent
- Remove duplicate package imports (identical options)
- Add non-breaking spaces before `\ref`, `\cite`, `\autoref` (in normal text only)

## NEVER Auto-Fix

- Math expression rewrites
- Document class changes
- Package replacements
- Bibliography backend changes
- Engine changes
- Shell escape enabling
- Publisher template structure modifications
- Semantic text edits

## Security Sandbox

When processing user-provided .zip or .tex files:

- **Zip Slip protection**: Reject absolute paths, `..` components, symlink escapes
- **Symlink removal**: Scan and remove all symbolic links after extraction
- **Shell escape**: Disabled by default; only report when `minted`/`gnuplottex` requires it
- **Sensitive paths**: Block access to home directory, SSH keys, environment variables
- **Executable restriction**: Project executables, Makefiles, pre/post scripts disabled by default
- **Resource limits**: Temp directory, read-only source copies, timeout, max log size
- **Security notes**: All warnings collected in `security-notes` section of reports

## Fix Levels

| Level | Behavior |
|-------|----------|
| `none` | No fixes applied (review-only) |
| `safe` | Only safe fixes (whitespace, blank lines, nobreak spaces) |
| `suggest` | Safe fixes + overfull box suggestions in comments |
| `aggressive` | All fixes including style changes (requires confirmation) |

## Compile Policies

| Policy | Behavior |
|--------|----------|
| `skip` | Skip compilation entirely |
| `try` | Attempt compilation, continue on failure |
| `required` | Fail if compilation fails |

## Write Policies

| Policy | Behavior |
|--------|----------|
| `report-only` | Only generate report, no file modifications |
| `copy` | Write optimized copy alongside original |
| `patch-only` | Only generate diff/patch file |

## CLI Usage

```bash
# Basic usage
python scripts/latex_optimizer.py --input paper.tex --mode single
python scripts/latex_optimizer.py --input project.zip --mode project
python scripts/latex_optimizer.py --input draft.tex --mode review
python scripts/latex_optimizer.py --input compile.log --mode log-review

# With build environment
python scripts/latex_optimizer.py --input paper.tex --build-env docker --docker-image texlive/texlive:2024
python scripts/latex_optimizer.py --input paper.tex --build-env tectonic

# With recipe selection
python scripts/latex_optimizer.py --input thesis.zip --recipe latexmk-xelatex
python scripts/latex_optimizer.py --input paper.tex --recipe pdflatex-biber

# With custom options
python scripts/latex_optimizer.py --input paper.tex --fix-level safe --compile-policy try
python scripts/latex_optimizer.py --input thesis.zip --engine xelatex --verbose
python scripts/latex_optimizer.py --input project.zip --config-file .latex-optimizer.yaml
python scripts/latex_optimizer.py --input paper.tex --compile-timeout 600
```

## Output Structure

### Single File
```
output/
├── optimized.tex
├── patch.diff
├── report.md
├── issue-summary.json
├── diagnostics.json
├── sarif.json
└── environment.json
```

### Project
```
output/
├── optimized-project.zip
├── patch.diff
├── report.md
├── issue-summary.json
├── diagnostics.json
├── sarif.json
├── project-graph.json
├── environment.json
├── compile-before.log
└── compile-after.log
```

### Review Only
```
output/
├── report.md
├── issue-summary.json
├── diagnostics.json
└── sarif.json
```

## Project Graph

The project graph (`project-graph.json`) maps all file dependencies:

```json
{
  "root": "main.tex",
  "nodes": [
    {"path": "main.tex", "node_type": "root", "dependencies": ["intro.tex", "method.tex"]},
    {"path": "intro.tex", "node_type": "sub-file", "dependencies": []},
    {"path": "refs.bib", "node_type": "bib", "dependencies": []},
    {"path": "figures/diagram.pdf", "node_type": "image", "dependencies": []}
  ],
  "magic_comments": {"program": "xelatex"}
}
```

## Configuration File

`.latex-optimizer.yaml` project-level settings:

```yaml
formatter: latexindent
fix_level: safe
compile_policy: try
build_env: local
compile_timeout: 300

recipes:
  my-custom-recipe:
    tools:
      - pdflatex
      - biber
      - pdflatex
      - pdflatex

diagnostics:
  output_sarif: true
  output_diagnostics: true
  output_annotations: false

security:
  sandbox_mode: true
  block_sensitive_paths: true
  block_executables: true

formatting:
  skip_environments:
    - minted
    - lstlisting
    - verbatim
  idempotency_check: true
  format_only_changed: false
```

## Reference Documents

- `references/workflow.md` - Detailed workflow descriptions
- `references/mode-routing.md` - Mode routing rules
- `references/issue-taxonomy.md` - Issue classification taxonomy
- `references/safe-fixes.md` - Safe fix checklist
- `references/unsafe-fixes.md` - High-risk operation checklist
- `references/tool-selection.md` - Tool selection guide
- `references/cjk-engine-guide.md` - CJK engine guide
- `references/overleaf-project-guide.md` - Overleaf project guide
- `references/review-only-guide.md` - Review-only mode guide
- `references/arxiv-publisher-checklist.md` - ArXiv submission checklist
- `references/report-template.md` - Report template

## Configuration Files

- `configs/latexindent-default.yaml` - latexindent default settings
- `configs/chktexrc-default` - chktex default settings
- `configs/latexmkrc-default` - latexmk default settings

## Environment Requirements

- Python 3.8+
- TeX Live (2020+) or MiKTeX (21.0+)
- latexmk
- latexindent (optional)
- chktex (optional)
- tex-fmt (optional)
- Docker (optional, for containerized builds)
- Tectonic (optional, for reproducible builds)

## Evolution Roadmap

### v0.2 (Current): Stability First
- ✅ Security sandbox + zip/path protection
- ✅ Project graph + root detection overhaul
- ✅ Unified diagnostics schema (diagnostics.json + sarif.json)
- ✅ Build recipes system
- ✅ Docker/Tectonic reproducible builds
- ✅ Dual formatter backend (latexindent + tex-fmt)
- ✅ Configuration file support (.latex-optimizer.yaml)
- ✅ Idempotency check for formatting
- ✅ Security notes in reports

### v0.3: Ecosystem Integration
- GitHub Action template
- Pre-commit hook
- Pinned TeXLive versions
- arara / latexmkrc / biber / makeindex detection
- PR comment templates
- SARIF upload examples

### v0.4: Intelligent Review
- TeXtidote / LanguageTool integration
- Citation/label/figure graph
- HTML report generation
- PR review annotations
- Regression corpus (Overleaf zip, arXiv source, CJK thesis, publisher templates)
- Formatting idempotency & false-modification tests