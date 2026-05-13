---
name: "latex-typeset-optimizer"
description: "Multi-mode LaTeX typeset optimizer: format, lint, compile, log-parse, safe-fix for .tex files and Overleaf projects. Invoke when optimizing LaTeX, fixing overfull boxes, checking compilation, or reviewing .tex/.zip projects."
---

# LaTeX Typeset Optimizer

A multi-mode LaTeX typeset optimization tool that supports single file optimization, Overleaf/LaTeX project optimization, compilation log analysis, and read-only review reports.

## Service Modes

| Mode | User Scenario | Modifies Files | Output Artifacts |
|------|--------------|----------------|------------------|
| **A. Single File** | Single `.tex` file or pasted LaTeX | Generates optimized copy, never overwrites original | `optimized.tex`, `patch.diff`, `report.md` |
| **B. Project** | Overleaf project zip | Modifies in working copy | `optimized-project.zip`, `patch.diff`, `report.md`, `issue-summary.json` |
| **C. Review Only** | User says "just check" / "don't modify" | No file modifications | `report.md`, `issue-summary.json` |

## When to Invoke

Invoke this skill when the user:
- Asks to optimize, format, or lint a LaTeX file
- Uploads a `.tex` file or Overleaf `.zip` project
- Wants to check for overfull/underfull boxes
- Needs compilation log analysis
- Asks for a review-only audit of LaTeX source
- Mentions LaTeX typesetting issues, bad boxes, undefined references

## Mode Routing Rules

The skill automatically detects the appropriate mode:

1. **Review-only triggers**: "只检查", "不要修改", "不要改文件", "只给报告", "review only", "audit only", "no edits", "no changes", "只审查", "仅检查", "不要动文件"
2. **Project triggers**: `.zip` input, "overleaf", "项目", "project", "论文", "thesis", "dissertation", "投稿", "submission", "arxiv"
3. **Log review**: `.log` file input
4. **Single file**: `.tex` file input (default)

## Workflow

### Single File Optimization

```
1. Intake: Copy .tex to temp workspace
2. Detect: Parse header, identify engine, packages, CJK usage
3. Tool Check: Verify latexindent/tex-fmt/chktex availability
4. Format: Apply latexindent or tex-fmt (with basic fallback)
5. Lint: Run chktex/lacheck if available
6. Compile: Execute latexmk with detected engine (try policy)
7. Parse Log: Extract errors, warnings, bad boxes, undefined refs
8. Classify: Categorize issues by severity (BLOCKING/HIGH/MEDIUM/LOW/INFO)
9. Safe Fix: Apply safe-level fixes (trailing whitespace, blank lines, nobreak spaces)
10. Generate Diff: Create unified diff between original and optimized
11. Report: Generate Markdown report + JSON issue summary
12. Output: optimized.tex, patch.diff, report.md, issue-summary.json
```

### Project Optimization

```
1. Intake: Unzip to temp workspace
2. Detect: Find main.tex, build dependency graph, detect engine/bib backend
3. Tool Check: Verify all required tools
4. Format: Format all .tex files in project
5. Lint: Lint all .tex files
6. Compile: Full latexmk build with bibliography
7. Parse Log: Parse compilation log
8. Classify: Classify all issues
9. Safe Fix: Apply safe fixes to all files
10. Generate Diff: Project-wide diff
11. Report: Generate comprehensive report
12. Package: Re-zip as optimized-project.zip
13. Output: optimized-project.zip, patch.diff, report.md, issue-summary.json
```

### Review-Only Mode

```
1. Intake: Copy input to workspace (read-only)
2. Detect: Analyze project structure
3. Compile: Try compilation to detect issues
4. Parse Log: Parse compilation log
5. Classify: Classify all issues
6. Report: Generate detailed review report
7. Output: report.md, issue-summary.json (NO file modifications)
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
python scripts/latex_optimizer.py --input paper.tex --mode single
python scripts/latex_optimizer.py --input project.zip --mode project
python scripts/latex_optimizer.py --input draft.tex --mode review
python scripts/latex_optimizer.py --input compile.log --mode log-review
python scripts/latex_optimizer.py --input paper.tex --fix-level safe --compile-policy try
python scripts/latex_optimizer.py --input thesis.zip --engine xelatex --verbose
```

## Output Structure

### Single File
```
output/
├── optimized.tex
├── patch.diff
├── report.md
└── issue-summary.json
```

### Project
```
output/
├── optimized-project.zip
├── patch.diff
├── report.md
├── issue-summary.json
├── compile-before.log
└── compile-after.log
```

### Review Only
```
output/
├── report.md
└── issue-summary.json
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
- TeX Live or MiKTeX
- latexmk
- latexindent (optional)
- chktex (optional)
- tex-fmt (optional)
