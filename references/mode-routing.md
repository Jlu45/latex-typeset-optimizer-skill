# Mode Routing Rules

## Automatic Mode Detection

The optimizer automatically detects the appropriate mode based on input type and user intent.

## Decision Tree

```
User Input
  │
  ├─ Check user intent keywords
  │   ├─ Review-only triggers → Mode: REVIEW_ONLY
  │   └─ Project triggers → Mode: PROJECT (if no review intent)
  │
  ├─ Check input file type
  │   ├─ .log → Mode: LOG_REVIEW
  │   ├─ .zip → Mode: PROJECT
  │   ├─ .tex → Check if part of project
  │   │   ├─ Has project indicators → Mode: PROJECT
  │   │   └─ Standalone → Mode: SINGLE_FILE
  │   └─ Directory → Mode: PROJECT
  │
  └─ Default → Mode: SINGLE_FILE
```

## Trigger Keywords

### Review-Only Triggers
- Chinese: 只检查, 不要修改, 不要改文件, 只给报告, 只审查, 仅检查, 不要动文件
- English: review only, audit only, no edits, no changes, don't modify, don't change, just check

### Project Triggers
- Chinese: 项目, 论文, 投稿
- English: overleaf, project, thesis, dissertation, submission, arxiv

## Mode Defaults

| Mode | Fix Level | Compile Policy | Write Policy |
|------|-----------|----------------|--------------|
| SINGLE_FILE | safe | try | copy |
| PROJECT | safe | try | copy |
| REVIEW_ONLY | none | try | report-only |
| LOG_REVIEW | none | skip | report-only |

## Project Indicators

A `.tex` file is considered part of a project if its parent directory contains any of:
- `figures/` directory
- `sections/` directory
- `chapters/` directory
- `bib/` directory
- `images/` directory
