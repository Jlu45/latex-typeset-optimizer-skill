#!/usr/bin/env python3
"""Project structure detector for LaTeX Typeset Optimizer"""

import re
from pathlib import Path
from typing import Dict, List, Optional

from models import ProjectInfo, TexHeader
from detect_main_tex import MainTexDetector


class ProjectDetector:
    def __init__(self):
        self.main_tex_detector = MainTexDetector()

    def analyze(self, workspace) -> ProjectInfo:
        info = ProjectInfo()

        root = workspace.root if hasattr(workspace, 'root') else Path(workspace)
        info.input_type = workspace.input_type.value if hasattr(workspace, 'input_type') else ""

        info.tex_files = self._find_tex_files(root)

        info.main_tex = self.main_tex_detector.detect(info.tex_files)

        if info.main_tex and info.main_tex.exists():
            header = self._parse_header(info.main_tex)
            info.document_class = header.document_class
            info.packages = header.packages

            info.engine_hint = self._detect_engine_hint(header)
            info.bib_backend = self._detect_bib_backend(header)
            info.uses_cjk = self._detect_cjk(header)
            info.uses_minted = 'minted' in header.packages
            info.uses_shell_escape = self._detect_shell_escape_need(header)

            info.dependencies = self._build_dependency_graph(info.main_tex)

        info.bib_files = self._find_bib_files(root)
        info.image_files = self._find_image_files(root)
        info.cls_files = self._find_cls_files(root)
        info.sty_files = self._find_sty_files(root)

        return info

    def _find_tex_files(self, root: Path) -> List[Path]:
        tex_files = []
        for ext in ['*.tex', '*.tikz']:
            tex_files.extend(root.rglob(ext))
        return sorted(tex_files)

    def _parse_header(self, tex_path: Path) -> TexHeader:
        header = TexHeader()
        try:
            content = tex_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return header

        header.content = content

        in_preamble = True
        for line in content.split('\n'):
            stripped = line.strip()

            if stripped.startswith('%!TEX'):
                header.magic_comments.append(stripped)

            if not in_preamble:
                break

            if stripped.startswith('%'):
                continue

            if r'\begin{document}' in line:
                in_preamble = False
                break

            docclass_match = re.match(
                r'\\documentclass(?:\[.*?\])?\{(\w+)\}', stripped
            )
            if docclass_match:
                header.document_class = docclass_match.group(1)

            pkg_match = re.match(
                r'\\usepackage(?:\[.*?\])?\{([^}]+)\}', stripped
            )
            if pkg_match:
                packages = [p.strip() for p in pkg_match.group(1).split(',')]
                header.packages.extend(packages)

        return header

    def _detect_engine_hint(self, header: TexHeader) -> Optional[str]:
        for line in header.magic_comments:
            lower = line.lower()
            if 'xelatex' in lower:
                return 'xelatex'
            if 'lualatex' in lower:
                return 'lualatex'
            if 'pdflatex' in lower:
                return 'pdflatex'

        cjk_packages = ['ctex', 'xeCJK', 'luatexja', 'kotex']
        if any(pkg in header.packages for pkg in cjk_packages):
            return 'xelatex'

        if 'fontspec' in header.packages:
            return 'xelatex'

        if 'pstricks' in header.packages:
            return 'xelatex'

        return None

    def _detect_bib_backend(self, header: TexHeader) -> str:
        if 'biblatex' in header.packages:
            for line in header.content.split('\n'):
                if 'biblatex' in line and 'backend=biber' in line:
                    return 'biber'
                if 'biblatex' in line and 'backend=bibtex' in line:
                    return 'bibtex'
            return 'biber'
        elif any(cmd in header.content for cmd in [r'\bibliography', r'\bibitem']):
            return 'bibtex'
        return 'bibtex'

    def _detect_cjk(self, header: TexHeader) -> bool:
        cjk_packages = ['ctex', 'xeCJK', 'luatexja', 'kotex', 'CJK', 'CJKutf8']
        return any(pkg in header.packages for pkg in cjk_packages)

    def _detect_shell_escape_need(self, header: TexHeader) -> bool:
        shell_escape_packages = ['minted', 'pythontex', 'sage']
        return any(pkg in header.packages for pkg in shell_escape_packages)

    def _build_dependency_graph(self, main_tex: Path) -> Dict[str, List[str]]:
        deps = {}
        try:
            content = main_tex.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return deps

        include_patterns = [
            (r'\\input\{([^}]+)\}', 'input'),
            (r'\\include\{([^}]+)\}', 'include'),
            (r'\\includegraphics(?:\[.*?\])?\{([^}]+)\}', 'image'),
            (r'\\bibliography\{([^}]+)\}', 'bibliography'),
            (r'\\addbibresource\{([^}]+)\}', 'bibresource'),
        ]

        for pattern, dep_type in include_patterns:
            matches = re.findall(pattern, content)
            if matches:
                deps[dep_type] = matches

        return deps

    def _find_bib_files(self, root: Path) -> List[Path]:
        return sorted(root.rglob('*.bib'))

    def _find_image_files(self, root: Path) -> List[Path]:
        images = []
        for ext in ['*.png', '*.jpg', '*.jpeg', '*.pdf', '*.eps', '*.svg']:
            images.extend(root.rglob(ext))
        return sorted(images)

    def _find_cls_files(self, root: Path) -> List[Path]:
        return sorted(root.rglob('*.cls'))

    def _find_sty_files(self, root: Path) -> List[Path]:
        return sorted(root.rglob('*.sty'))
