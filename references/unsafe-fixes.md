# High-Risk Operations

The following operations require explicit user confirmation and are NEVER applied automatically.

## 1. Changing Document Class
- **Risk**: May completely alter document layout and formatting
- **Example**: Changing `article` to `report` changes section numbering
- **Action**: Only change if user explicitly requests it

## 2. Adding/Removing Packages
- **Risk**: May introduce package conflicts or remove needed functionality
- **Example**: Adding `hyperref` last vs. first can break other packages
- **Action**: Suggest but never auto-apply

## 3. Modifying Math Expressions
- **Risk**: May change mathematical meaning
- **Example**: Changing `\frac12` to `\frac{1}{2}` is safe, but reordering terms is not
- **Action**: Only cosmetic changes in suggest mode

## 4. Enabling Shell Escape
- **Risk**: Security vulnerability - allows arbitrary command execution
- **Example**: Required by `minted`, `pythontex`, `sage`
- **Action**: Warn user about security implications, require explicit confirmation

## 5. Changing Bibliography Backend
- **Risk**: May break existing bibliography setup
- **Example**: Switching from bibtex to biber requires different `\bibliography` syntax
- **Action**: Never auto-change, only suggest

## 6. Modifying Publisher Templates
- **Risk**: May violate submission requirements
- **Example**: IEEE, ACM, Elsevier templates have strict formatting rules
- **Action**: Only review, never modify template structure

## 7. Rewriting Paragraph Content
- **Risk**: Beyond typesetting scope, may change meaning
- **Example**: "Improving" sentence structure
- **Action**: Out of scope - only fix typesetting issues

## 8. Automatic Overfull Box Fixes
- **Risk**: May break intentional layout
- **Example**: A wide table may be intentionally overflowing
- **Action**: Only suggest fixes, add comments in suggest mode

## Confirmation Protocol

When an aggressive fix is suggested:
1. Show the proposed change with diff
2. Explain the risk
3. Ask for explicit user confirmation
4. Apply only if confirmed
5. Record the change in the report
