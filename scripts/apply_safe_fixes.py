#!/usr/bin/env python3
"""Safe fix applicator for LaTeX Typeset Optimizer"""

import re
from pathlib import Path
from typing import List, Optional

from models import Issue, FixLevel, FixResult


class SafeFixer:
    SAFE_FIXES = [
        'trim-trailing-whitespace',
        'normalize-blank-lines',
        'ensure-final-newline',
        'reindent-environments',
        'remove-duplicate-packages',
        'add-nobreak-before-ref',
        'fix-common-typos'
    ]

    def __init__(self, fix_level: FixLevel = FixLevel.SAFE):
        self.fix_level = fix_level
        self.applied_fixes = []

    def apply_fixes(self, tex_path: Path,
                    issues: List[Issue]) -> FixResult:
        if self.fix_level == FixLevel.NONE:
            return FixResult(applied=[], modified=False, failed=[])

        self.applied_fixes = []

        try:
            content = tex_path.read_text(encoding='utf-8')
        except Exception:
            return FixResult(applied=[], modified=False, failed=['read-file'])

        original_content = content

        if self.fix_level in [FixLevel.SAFE, FixLevel.SUGGEST, FixLevel.AGGRESSIVE]:
            content = self._trim_trailing_whitespace(content)
            content = self._normalize_blank_lines(content)
            content = self._ensure_final_newline(content)

        if self.fix_level in [FixLevel.SAFE, FixLevel.SUGGEST, FixLevel.AGGRESSIVE]:
            content = self._add_nobreak_spaces(content)

        if self.fix_level in [FixLevel.SUGGEST, FixLevel.AGGRESSIVE]:
            content = self._suggest_overfull_fixes(content, issues)

        if self.fix_level == FixLevel.AGGRESSIVE:
            content = self._remove_duplicate_packages(content)

        modified = content != original_content

        if modified:
            try:
                tex_path.write_text(content, encoding='utf-8')
            except Exception:
                return FixResult(
                    applied=self.applied_fixes,
                    modified=False,
                    failed=['write-file']
                )

        return FixResult(
            applied=self.applied_fixes,
            modified=modified,
            failed=[]
        )

    def _trim_trailing_whitespace(self, content: str) -> str:
        lines = content.split('\n')
        cleaned = [line.rstrip() for line in lines]
        if cleaned != lines:
            self.applied_fixes.append('trim-trailing-whitespace')
        return '\n'.join(cleaned)

    def _normalize_blank_lines(self, content: str) -> str:
        normalized = re.sub(r'\n{3,}', '\n\n', content)
        if normalized != content:
            self.applied_fixes.append('normalize-blank-lines')
        return normalized

    def _ensure_final_newline(self, content: str) -> str:
        if content and not content.endswith('\n'):
            self.applied_fixes.append('ensure-final-newline')
            return content + '\n'
        return content

    def _add_nobreak_spaces(self, content: str) -> str:
        patterns = [
            (r'(\w) \\ref\{', r'\1~\\ref{'),
            (r'(\w) \\cite\{', r'\1~\\cite{'),
            (r'(\w) \\autoref\{', r'\1~\\autoref{'),
            (r'(\w) \\eqref\{', r'\1~\\eqref{'),
            (r'(\w) \\Cref\{', r'\1~\\Cref{'),
            (r'(\w) \\cref\{', r'\1~\\cref{'),
        ]

        modified = False
        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                modified = True

        if modified:
            self.applied_fixes.append('add-nobreak-before-ref')

        return content

    def _suggest_overfull_fixes(self, content: str,
                                issues: List[Issue]) -> str:
        overfull_lines = set()
        for issue in issues:
            if issue.category == 'overfull-box' and issue.line:
                overfull_lines.add(issue.line)

        if not overfull_lines:
            return content

        lines = content.split('\n')
        modified = False

        for line_num in overfull_lines:
            idx = line_num - 1
            if 0 <= idx < len(lines):
                if not lines[idx].strip().startswith('%'):
                    lines[idx] = f"% OPTIMIZE: overfull box detected at this line\n{lines[idx]}"
                    modified = True

        if modified:
            self.applied_fixes.append('suggest-overfull-fixes')

        return '\n'.join(lines)

    def _remove_duplicate_packages(self, content: str) -> str:
        packages_seen = {}
        lines = content.split('\n')
        new_lines = []
        modified = False

        for line in lines:
            match = re.match(r'\\usepackage(?:\[.*?\])?\{([^}]+)\}', line.strip())
            if match:
                key = line.strip()
                if key in packages_seen:
                    modified = True
                    continue
                packages_seen[key] = True
            new_lines.append(line)

        if modified:
            self.applied_fixes.append('remove-duplicate-packages')

        return '\n'.join(new_lines)
