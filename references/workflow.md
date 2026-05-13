# Workflow

## Single File Optimization Workflow

```
Input: .tex file
  │
  ├─ 1. Intake: Copy to temp workspace, preserve original
  ├─ 2. Detect: Parse header → engine, packages, CJK
  ├─ 3. Tool Check: Verify latexindent/tex-fmt/chktex
  ├─ 4. Format: latexindent → tex-fmt → basic fallback
  ├─ 5. Lint: chktex → lacheck → basic lint
  ├─ 6. Compile: latexmk with detected engine
  ├─ 7. Parse Log: Extract errors/warnings/bad boxes
  ├─ 8. Classify: Severity-based issue categorization
  ├─ 9. Safe Fix: Whitespace, blank lines, nobreak spaces
  ├─ 10. Diff: Unified diff between original and optimized
  ├─ 11. Report: Markdown report + JSON summary
  └─ 12. Output: optimized.tex, patch.diff, report.md, issue-summary.json
```

## Project Optimization Workflow

```
Input: .zip file or directory
  │
  ├─ 1. Intake: Unzip to temp workspace
  ├─ 2. Detect: Find main.tex, build dependency graph
  ├─ 3. Tool Check: Verify all required tools
  ├─ 4. Format: Format all .tex files
  ├─ 5. Lint: Lint all .tex files
  ├─ 6. Compile: Full latexmk build
  ├─ 7. Parse Log: Parse compilation log
  ├─ 8. Classify: Classify all issues
  ├─ 9. Safe Fix: Apply fixes to all files
  ├─ 10. Diff: Project-wide diff
  ├─ 11. Report: Comprehensive report
  ├─ 12. Package: Re-zip as optimized-project.zip
  └─ 13. Output: optimized-project.zip, patch.diff, report.md, issue-summary.json
```

## Review-Only Workflow

```
Input: .tex or .zip (with review intent)
  │
  ├─ 1. Intake: Copy to workspace (read-only)
  ├─ 2. Detect: Analyze project structure
  ├─ 3. Compile: Try compilation
  ├─ 4. Parse Log: Parse compilation log
  ├─ 5. Classify: Classify all issues
  ├─ 6. Report: Detailed review report
  └─ 7. Output: report.md, issue-summary.json (NO file modifications)
```

## Log-Review Workflow

```
Input: .log file
  │
  ├─ 1. Intake: Copy log to workspace
  ├─ 2. Parse Log: Extract all issues
  ├─ 3. Classify: Categorize by severity
  ├─ 4. Report: Log analysis report
  └─ 5. Output: report.md, issue-summary.json
```
