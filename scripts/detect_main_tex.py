#!/usr/bin/env python3
"""Main tex file detector for LaTeX Typeset Optimizer"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class MainTexDetector:
    PRIORITY_NAMES = ['main.tex', 'paper.tex', 'thesis.tex', 'dissertation.tex',
                      'article.tex', 'report.tex', 'book.tex', 'slides.tex',
                      'root.tex', 'document.tex']

    MAGIC_ROOT_PATTERN = re.compile(r'^%\s*!TEX\s+root\s*=\s*(.+?)\s*$', re.MULTILINE)
    MAGIC_PROGRAM_PATTERN = re.compile(r'^%\s*!TEX\s+program\s*=\s*(.+?)\s*$', re.MULTILINE)

    def detect(self, tex_files: List[Path]) -> Optional[Path]:
        main_tex, _ = self.detect_with_hints(tex_files)
        return main_tex

    def detect_with_hints(self, tex_files: List[Path]) -> Tuple[Optional[Path], Dict[str, str]]:
        magic_comments: Dict[str, str] = {}

        if not tex_files:
            return None, magic_comments

        root_via_magic = self._find_root_via_magic_comment(tex_files)
        if root_via_magic:
            magic_comments["root"] = str(root_via_magic)

        for tex_file in tex_files:
            file_magic = self._scan_magic_comments(tex_file)
            for key, value in file_magic.items():
                if key not in magic_comments:
                    magic_comments[key] = value

        if root_via_magic:
            return root_via_magic, magic_comments

        if len(tex_files) == 1:
            return tex_files[0], magic_comments

        candidates = []
        for tex_file in tex_files:
            score = self._score_file(tex_file)
            candidates.append((tex_file, score))

        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0], magic_comments

    def _find_root_via_magic_comment(self, tex_files: List[Path]) -> Optional[Path]:
        for tex_file in tex_files:
            try:
                content = tex_file.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue
            match = self.MAGIC_ROOT_PATTERN.search(content)
            if match:
                root_path_str = match.group(1).strip()
                root_path = (tex_file.parent / root_path_str).resolve()
                if root_path.exists():
                    return root_path
        return None

    def _scan_magic_comments(self, tex_path: Path) -> Dict[str, str]:
        result: Dict[str, str] = {}
        try:
            content = tex_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return result

        root_match = self.MAGIC_ROOT_PATTERN.search(content)
        if root_match:
            result["root"] = root_match.group(1).strip()

        program_match = self.MAGIC_PROGRAM_PATTERN.search(content)
        if program_match:
            result["program"] = program_match.group(1).strip()

        return result

    def _score_file(self, tex_path: Path) -> float:
        score = 0.0

        if tex_path.name.lower() in self.PRIORITY_NAMES:
            score += 100

        try:
            content = tex_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return score

        if r'\documentclass' in content:
            score += 50

        if r'\begin{document}' in content:
            score += 30

        if r'\end{document}' in content:
            score += 10

        input_count = content.count(r'\input{') + content.count(r'\include{')
        if input_count == 0:
            score += 5

        include_count = content.count(r'\include{')
        if include_count > 0:
            score += 20

        score += len(content) / 1000

        return score
