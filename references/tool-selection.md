# Tool Selection Guide

## Available Tools

### Formatters

| Tool | Priority | Notes |
|------|----------|-------|
| latexindent | 1st choice | Most configurable, Perl-based |
| tex-fmt | 2nd choice | Fast, Rust-based, less configurable |
| basic (built-in) | Fallback | Trailing whitespace, blank lines, final newline |

### Linters

| Tool | Priority | Notes |
|------|----------|-------|
| chktex | 1st choice | Most common LaTeX linter |
| lacheck | 2nd choice | Simpler, faster |
| basic (built-in) | Fallback | Trailing whitespace, nobreak space suggestions |

### Compilers

| Tool | Priority | Notes |
|------|----------|-------|
| latexmk | Required | Automates multi-pass compilation |
| pdflatex | Default engine | Standard LaTeX engine |
| xelatex | CJK/fontspec | Required for CJK and system fonts |
| lualatex | Advanced features | Lua scripting, Unicode |

### Bibliography Tools

| Tool | Priority | Notes |
|------|----------|-------|
| biber | biblatex default | Modern bibliography processor |
| bibtex | Traditional | Legacy bibliography processor |

## Tool Selection Logic

### Formatter Selection
```
if latexindent available → use latexindent
elif tex-fmt available → use tex-fmt
else → use basic formatter
```

### Engine Selection
```
if user specified --engine → use specified engine
elif %!TEX program magic comment → use specified engine
elif CJK packages detected (ctex, xeCJK, etc.) → use xelatex
elif fontspec detected → use xelatex
elif pstricks detected → use xelatex
else → use pdflatex
```

### Bibliography Tool Selection
```
if biblatex with backend=biber → use biber
elif biblatex (no backend specified) → use biber (default for biblatex)
elif \bibliography or \bibitem → use bibtex
else → use bibtex (default)
```

## Tool Availability Check

The optimizer checks tool availability at startup:
1. Try `tool --version` first
2. Fall back to `which`/`where` command
3. Mark unavailable tools and use alternatives
4. Report tool status in verbose mode
