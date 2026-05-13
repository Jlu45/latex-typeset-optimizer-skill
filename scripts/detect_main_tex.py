#!/usr/bin/env python3
"""Main tex file detector for LaTeX Typeset Optimizer"""

from pathlib import Path
from typing import List, Optional


class MainTexDetector:
    PRIORITY_NAMES = ['main.tex', 'paper.tex', 'thesis.tex', 'dissertation.tex',
                      'article.tex', 'report.tex', 'book.tex', 'slides.tex',
                      'root.tex', 'document.tex']

    def detect(self, tex_files: List[Path]) -> Optional[Path]:
        if not tex_files:
            return None

        if len(tex_files) == 1:
            return tex_files[0]

        candidates = []
        for tex_file in tex_files:
            score = self._score_file(tex_file)
            candidates.append((tex_file, score))

        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]

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
