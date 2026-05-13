# ArXiv Publisher Checklist

## Pre-Submission Checklist

Use this checklist when preparing a LaTeX document for ArXiv submission.

### Compilation

- [ ] Document compiles without errors
- [ ] No undefined references
- [ ] No undefined citations
- [ ] All figures included and referenced
- [ ] Bibliography compiles correctly
- [ ] No overfull boxes (or acceptable ones)

### File Structure

- [ ] Main file is `main.tex` or `paper.tex`
- [ ] All included files are present
- [ ] All figure files are included
- [ ] Bibliography file (.bib) is included
- [ ] Custom class/style files are included
- [ ] No absolute file paths used

### Engine Compatibility

- [ ] Engine specified in magic comment: `%!TEX program = pdflatex`
- [ ] Or use ArXiv-compatible engine
- [ ] CJK documents use xelatex (ArXiv supports it)
- [ ] No shell-escape required

### Package Considerations

- [ ] All packages are in standard TeX Live
- [ ] No proprietary packages
- [ ] `hyperref` loaded last (usually)
- [ ] No conflicting package options
- [ ] `microtype` recommended for better typography

### Formatting

- [ ] No trailing whitespace
- [ ] Consistent indentation
- [ ] No duplicate package imports
- [ ] Non-breaking spaces before references
- [ ] Proper use of `~` before `\cite` and `\ref`

### Common ArXiv Issues

1. **File size limit**: 10MB for single submission
2. **Figure formats**: PDF, PNG, JPG preferred (no EPS for pdflatex)
3. **Font embedding**: All fonts must be embedded in PDF
4. **Bibliography**: Use bibtex (biber may not work on ArXiv)
5. **Custom fonts**: Not supported, use standard fonts
6. **Shell escape**: Not available on ArXiv
7. **minted**: Not supported (requires shell escape)

### ArXiv-Specific Checks

```bash
# Check compilation
latexmk -pdf main.tex

# Check for undefined references
grep -c "undefined" main.log

# Check for overfull boxes
grep -c "Overfull" main.log

# Verify all figures exist
grep "includegraphics" main.tex | ...

# Check total file size
du -sh .
```

### Recommended Pre-Submission Optimization

```bash
# Run review mode first
python scripts/latex_optimizer.py --input paper.zip --mode review

# Fix issues, then optimize
python scripts/latex_optimizer.py --input paper.zip --mode project --fix-level safe

# Final review
python scripts/latex_optimizer.py --input optimized-project.zip --mode review
```
