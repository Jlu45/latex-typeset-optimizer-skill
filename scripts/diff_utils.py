#!/usr/bin/env python3
"""Diff generation utilities for LaTeX Typeset Optimizer"""

import difflib
import os
from pathlib import Path
from typing import Optional


class DiffGenerator:
    def generate_diff(self, original_path: str, modified_path: str,
                      context_lines: int = 3) -> Optional[str]:
        try:
            with open(original_path, 'r', encoding='utf-8', errors='ignore') as f:
                original_lines = f.readlines()
        except Exception:
            return None

        try:
            with open(modified_path, 'r', encoding='utf-8', errors='ignore') as f:
                modified_lines = f.readlines()
        except Exception:
            return None

        diff = difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=os.path.basename(original_path),
            tofile=os.path.basename(modified_path),
            n=context_lines
        )

        diff_text = ''.join(diff)
        return diff_text if diff_text else None

    def generate_diff_from_strings(self, original: str, modified: str,
                                   original_name: str = "original",
                                   modified_name: str = "optimized",
                                   context_lines: int = 3) -> Optional[str]:
        original_lines = original.splitlines(keepends=True)
        modified_lines = modified.splitlines(keepends=True)

        diff = difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=original_name,
            tofile=modified_name,
            n=context_lines
        )

        diff_text = ''.join(diff)
        return diff_text if diff_text else None

    def generate_project_diff(self, workspace_root: Path,
                              context_lines: int = 3) -> Optional[str]:
        all_diffs = []

        original_files = list(workspace_root.rglob('*_original.tex'))
        for orig_file in sorted(original_files):
            stem = orig_file.stem.replace('_original', '')
            modified_file = orig_file.parent / f"{stem}.tex"

            if modified_file.exists():
                diff = self.generate_diff(
                    str(orig_file), str(modified_file), context_lines
                )
                if diff:
                    all_diffs.append(diff)

        if not all_diffs:
            return None

        return '\n'.join(all_diffs)

    def get_diff_stats(self, diff_text: str) -> dict:
        if not diff_text:
            return {"added": 0, "removed": 0, "changed": 0}

        added = 0
        removed = 0

        for line in diff_text.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                added += 1
            elif line.startswith('-') and not line.startswith('---'):
                removed += 1

        return {
            "added": added,
            "removed": removed,
            "changed": min(added, removed)
        }
