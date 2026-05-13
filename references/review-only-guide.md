# Review-Only Mode Guide

## Overview

Review-only mode analyzes LaTeX documents without making any modifications. It produces a detailed report of all detected issues.

## When to Use

- User says "只检查" / "不要修改" / "review only"
- User wants to audit a document before making changes
- Checking a document for submission readiness
- Analyzing compilation logs

## Behavior

### What Review Mode Does
- Copies input to temporary workspace
- Analyzes project structure
- Attempts compilation (with `try` policy)
- Parses compilation logs
- Runs linters
- Classifies all issues by severity
- Generates detailed report

### What Review Mode Does NOT Do
- Does NOT modify any source files
- Does NOT apply any fixes (fix-level = none)
- Does NOT generate optimized copies
- Does NOT create diff/patch files

## Output

```
output/
├── report.md          # Detailed review report
└── issue-summary.json # Structured issue data
```

## Report Contents

1. **Executive Summary** - High-level overview of document health
2. **Compilation Status** - Whether the document compiles successfully
3. **Issue Statistics** - Count of issues by severity level
4. **Detailed Issues** - Full list with locations and recommendations
5. **Recommendations** - Prioritized action items

## Trigger Keywords

### Chinese
- 只检查
- 不要修改
- 不要改文件
- 只给报告
- 只审查
- 仅检查
- 不要动文件

### English
- review only
- audit only
- no edits
- no changes
- don't modify
- don't change
- just check
- check only

## Example Usage

```bash
# Review a single file
python scripts/latex_optimizer.py --input paper.tex --mode review

# Review a project
python scripts/latex_optimizer.py --input project.zip --mode review

# Review with verbose output
python scripts/latex_optimizer.py --input draft.tex --mode review --verbose
```

## Integration with Other Modes

Review-only mode can be used as a first step before optimization:
1. Run review mode to identify issues
2. Review the report
3. Decide which issues to fix
4. Run optimization mode with appropriate fix level
