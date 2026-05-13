# Overleaf Project Guide

## Overview

Overleaf projects exported as `.zip` files require special handling to preserve structure and functionality.

## Zip Structure

### Standard Overleaf Export
```
project-name.zip
├── main.tex
├── references.bib
├── figures/
│   ├── fig1.pdf
│   └── fig2.png
├── sections/
│   ├── intro.tex
│   ├── method.tex
│   └── results.tex
├── supplementary.tex
└── custom-style.cls
```

### Nested Directory Export
Some Overleaf exports have a single root directory:
```
project-name.zip
└── project-name/
    ├── main.tex
    ├── references.bib
    └── ...
```
The optimizer automatically detects and flattens this structure.

## Processing Steps

1. **Unzip** to temporary workspace
2. **Detect main.tex** using scoring algorithm
3. **Build dependency graph** from `\input`/`\include` commands
4. **Detect engine** from magic comments and packages
5. **Detect bibliography backend** from package options
6. **Process all .tex files** (format, lint, fix)
7. **Compile** with latexmk
8. **Re-package** preserving original structure

## Main File Detection Priority

1. `main.tex` → highest priority
2. `paper.tex`, `thesis.tex` → high priority
3. File containing `\documentclass` → medium priority
4. File containing `\begin{document}` → medium priority
5. Largest .tex file → low priority tiebreaker

## Common Overleaf Patterns

### latexmkrc
Overleaf projects may include `.latexmkrc` for custom build settings:
```perl
$pdflatex = 'pdflatex --shell-escape %O %S';
```

### clsi (Overleaf build system)
- Overleaf uses its own build system (clsi)
- Some features may not work locally (e.g., `latexmkrc`)
- The optimizer handles this gracefully

### Special Files
- `.latexmkrc` - Build configuration
- `.chktexrc` - Linting configuration
- `latexmkrc` - Alternative build config (no dot prefix)

## Output Packaging

The optimizer creates an output zip that:
- Preserves original directory structure
- Excludes auxiliary files (.aux, .log, .synctex.gz, etc.)
- Excludes `_original.tex` backup copies
- Includes only source files and resources
- Maintains UTF-8 encoding

## Known Issues

### minted Package
- Requires `--shell-escape` flag
- Security risk - optimizer warns user before enabling
- Alternative: use `listings` package

### Shell Escape
- Some packages require `--shell-escape`
- The optimizer does NOT enable this automatically
- User must explicitly confirm

### Large Projects
- Compilation timeout: 5 minutes
- May need to increase for very large projects
- Use `--compile-policy skip` to skip compilation

### Custom Classes
- `.cls` files are preserved as-is
- The optimizer does not modify class files
- Custom classes may affect compilation behavior
