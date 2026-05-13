# CJK Engine Guide

## Overview

CJK (Chinese, Japanese, Korean) documents require special engine handling. This guide covers engine selection and common CJK-related issues.

## Engine Recommendations

| Language | Recommended Engine | Package | Notes |
|----------|-------------------|---------|-------|
| Chinese (Simplified) | xelatex | ctex | Best CJK support |
| Chinese (Traditional) | xelatex | ctex | Use `fontset=none` for custom fonts |
| Japanese | xelatex | luatexja | lualatex also works |
| Korean | xelatex | kotex | xetex-ko also available |
| Mixed CJK+English | xelatex | ctex + fontspec | Use xeCJK for fine control |

## Detection Rules

### Automatic Detection
The optimizer detects CJK requirements from:
1. **Magic comments**: `%!TEX program = xelatex`
2. **CJK packages**: ctex, xeCJK, CJK, CJKutf8, luatexja, kotex
3. **Font packages**: fontspec (indicates xelatex/lualatex)
4. **CJK characters in source**: Unicode CJK range detection

### Engine Fallback
```
CJK detected → try xelatex
  ├─ xelatex available → use xelatex
  ├─ lualatex available → use lualatex
  └─ only pdflatex → warn user (CJK may not work)
```

## Common CJK Issues

### Font Not Found
- **Symptom**: `Font ... not found`
- **Fix**: Install CJK fonts or use `fontset=none` with custom fonts
- **Example**: `\usepackage[fontset=none]{ctex}` + `\setCJKmainfont{SimSun}`

### Encoding Issues
- **Symptom**: Garbled characters
- **Fix**: Ensure file is UTF-8 encoded, use xelatex
- **Note**: pdflatex + CJKutf8 is possible but not recommended

### Line Breaking
- **Symptom**: CJK text not breaking at line ends
- **Fix**: Use ctex package (handles CJK line breaking automatically)

### Overfull Boxes with CJK
- **Symptom**: More overfull boxes than expected
- **Fix**: Use `\sloppy` or adjust `\emergencystretch`
- **Note**: CJK line breaking is less flexible than English

## ctex Package Options

```latex
\usepackage{ctex}                    % Auto-detect, use xelatex
\usepackage[fontset=auto]{ctex}      % Auto-select font set
\usepackage[fontset=none]{ctex}      % Manual font configuration
\usepackage[fontset=windows]{ctex}   % Windows fonts
\usepackage[fontset=mac]{ctex}       % macOS fonts
\usepackage[fontset=ubuntu]{ctex}    % Ubuntu fonts
\usepackage[fontset=fandol]{ctex}    % Fandol fonts (TeX Live)
```

## xeCJK Fine Control

```latex
\usepackage{xeCJK}
\setCJKmainfont{SimSun}
\setCJKsansfont{SimHei}
\setCJKmonofont{FangSong}
\setCJKfamilyfont{zhkai}{KaiTi}
```
