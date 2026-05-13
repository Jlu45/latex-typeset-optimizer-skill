# Issue Taxonomy

## Severity Levels

| Level | Description | Action Required |
|-------|-------------|-----------------|
| BLOCKING | Prevents compilation | Must fix immediately |
| HIGH | Affects document integrity | Should fix before submission |
| MEDIUM | Affects visual quality | Nice to fix |
| LOW | Minor quality issue | Optional |
| INFO | Style suggestion | Discretionary |

## Issue Categories

### BLOCKING

| Code | Description | Example | Recommendation |
|------|-------------|---------|----------------|
| compile-error | General compilation error | Missing `$` inserted | Fix the syntax error |
| undefined-control-sequence | Unknown command | `Undefined control sequence \foo` | Check spelling or add required package |
| missing-file | Referenced file not found | `File 'xxx.sty' not found` | Install package or fix path |

### HIGH

| Code | Description | Example | Recommendation |
|------|-------------|---------|----------------|
| missing-package | Required package not available | `Package foo not found` | Install the package |
| undefined-reference | Label referenced but not defined | `Reference 'fig:1' undefined` | Add `\label` or fix reference |
| undefined-citation | Citation key not found | `Citation 'smith2020' undefined` | Check .bib file or run bibtex/biber |

### MEDIUM

| Code | Description | Example | Recommendation |
|------|-------------|---------|----------------|
| overfull-box | Content exceeds box width | `Overfull \hbox (10pt too wide)` | Adjust text or use `\sloppy` |
| compile-warning | Compilation warning | `Rerun to get cross-references right` | Recompile |

### LOW

| Code | Description | Example | Recommendation |
|------|-------------|---------|----------------|
| underfull-box | Box not filled enough | `Underfull \hbox (badness 10000)` | Adjust spacing |
| spacing-issue | Non-optimal spacing | Missing non-breaking space before `\ref` | Add `~` before references |
| font-warning | Font substitution | `Font shape substitution` | Install missing fonts |

### INFO

| Code | Description | Example | Recommendation |
|------|-------------|---------|----------------|
| style-issue | Code style issue | Trailing whitespace | Clean up formatting |
| lint-chktex | chktex finding | Various style warnings | Review and fix |
| lint-lacheck | lacheck finding | Various style warnings | Review and fix |
