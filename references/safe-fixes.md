# Safe Fixes Checklist

The following fixes can be automatically applied at the **safe** fix level.

## Whitespace

- **Trim trailing whitespace** - Remove spaces and tabs at end of lines
- **Normalize consecutive blank lines** - Reduce 3+ consecutive blank lines to 2
- **Ensure final newline** - Add trailing newline if missing

## Indentation

- **Re-indent environments** - Use latexindent to fix environment indentation
- **Preserve verbatim/minted** - Never modify content inside verbatim environments

## Low-Risk Reference Fixes

- **Add non-breaking spaces before `\ref`** - Replace `word \ref{...}` with `word~\ref{...}`
- **Add non-breaking spaces before `\cite`** - Replace `word \cite{...}` with `word~\cite{...}`
- **Add non-breaking spaces before `\autoref`** - Replace `word \autoref{...}` with `word~\autoref{...}`
- **Add non-breaking spaces before `\eqref`** - Replace `word \eqref{...}` with `word~\eqref{...}`
- **Add non-breaking spaces before `\Cref`/`\cref`** - Same pattern for cleveref commands

**Important**: Only apply in normal text context. Do NOT apply in:
- Math environments (`$...$`, `\[...\]`)
- Macro definitions (`\newcommand`, `\def`)
- Fragile content (verbatim, minted, lstlisting)

## Duplicate Removal

- **Remove duplicate package imports** - Delete identical consecutive `\usepackage` lines
  - Only when options are exactly the same
  - Preserve different option variants

## NEVER Auto-Fix

The following are explicitly excluded from safe fixes:

- Math expression rewrites
- Document class changes
- Package replacements or additions
- Bibliography backend changes (bibtex ↔ biber)
- Engine changes
- Shell escape enabling
- Publisher template structure modifications
- Semantic text edits
- Automatic overfull box fixes (layout may be intentional)
