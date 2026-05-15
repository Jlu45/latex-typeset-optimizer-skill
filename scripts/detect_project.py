#!/usr/bin/env python3
"""Project structure detector for LaTeX Typeset Optimizer"""

import re
from pathlib import Path
from typing import Dict, List, Optional

from models import ProjectInfo, ProjectGraph, ProjectGraphNode, TexHeader
from detect_main_tex import MainTexDetector


class ProjectDetector:
    MAGIC_COMMENT_PATTERNS = {
        'root': re.compile(r'^%\s*!TEX\s+root\s*=\s*(.+?)\s*$', re.MULTILINE),
        'program': re.compile(r'^%\s*!TEX\s+program\s*=\s*(.+?)\s*$', re.MULTILINE),
        'recipe': re.compile(r'^%\s*!LW\s+recipe\s*=\s*(.+?)\s*$', re.MULTILINE),
    }
    ARARA_PATTERN = re.compile(r'^%\s*arara:\s*(.+?)\s*$', re.MULTILINE)

    def __init__(self):
        self.main_tex_detector = MainTexDetector()

    def analyze(self, workspace) -> ProjectInfo:
        info = ProjectInfo()

        root = workspace.root if hasattr(workspace, 'root') else Path(workspace)
        info.input_type = workspace.input_type.value if hasattr(workspace, 'input_type') else ""

        info.tex_files = self._find_tex_files(root)

        main_tex, magic_comments = self.main_tex_detector.detect_with_hints(info.tex_files)
        info.main_tex = main_tex

        all_magic = self._collect_all_magic_comments(info.tex_files)
        for key, value in magic_comments.items():
            if key not in all_magic:
                all_magic[key] = value
        info.magic_comments = all_magic

        info.arara_directives = self._collect_arara_directives(info.tex_files)

        info.has_latexmkrc = self._check_latexmkrc(root)

        if info.main_tex and info.main_tex.exists():
            header = self._parse_header(info.main_tex)
            info.document_class = header.document_class
            info.packages = header.packages

            info.engine_hint = self._detect_engine_hint(header)
            if "program" in info.magic_comments:
                info.engine_hint = info.magic_comments["program"]
            info.bib_backend = self._detect_bib_backend(header)
            info.uses_cjk = self._detect_cjk(header)
            info.uses_minted = 'minted' in header.packages
            info.uses_shell_escape = self._detect_shell_escape_need(header)

            info.dependencies = self._build_dependency_graph(info.main_tex)

        info.bib_files = self._find_bib_files(root)
        info.image_files = self._find_image_files(root)
        info.cls_files = self._find_cls_files(root)
        info.sty_files = self._find_sty_files(root)

        info.project_graph = self.build_project_graph(info, root)

        return info

    def _collect_all_magic_comments(self, tex_files: List[Path]) -> Dict[str, str]:
        result: Dict[str, str] = {}
        for tex_file in tex_files:
            try:
                content = tex_file.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue
            for key, pattern in self.MAGIC_COMMENT_PATTERNS.items():
                match = pattern.search(content)
                if match and key not in result:
                    result[key] = match.group(1).strip()
        return result

    def _collect_arara_directives(self, tex_files: List[Path]) -> List[str]:
        directives: List[str] = []
        for tex_file in tex_files:
            try:
                content = tex_file.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue
            matches = self.ARARA_PATTERN.findall(content)
            directives.extend(matches)
        return directives

    def _check_latexmkrc(self, root: Path) -> bool:
        return (root / '.latexmkrc').exists() or (root / 'latexmkrc').exists()

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

            if stripped.startswith('%!TEX') or stripped.startswith('% !TEX'):
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
            (r'\\subfile\{([^}]+)\}', 'subfile'),
            (r'\\import\{([^}]+)\}\{([^}]+)\}', 'import'),
            (r'\\subimport\{([^}]+)\}\{([^}]+)\}', 'subimport'),
            (r'\\graphicspath\{([^}]+)\}', 'graphicspath'),
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

    def build_project_graph(self, info: ProjectInfo, root: Path) -> ProjectGraph:
        nodes = []

        for tex in info.tex_files:
            nodes.append(ProjectGraphNode(
                path=tex,
                file_type='tex',
                is_main=(tex == info.main_tex),
            ))

        for bib in info.bib_files:
            nodes.append(ProjectGraphNode(path=bib, file_type='bib'))

        for img in info.image_files:
            nodes.append(ProjectGraphNode(path=img, file_type='image'))

        for cls in info.cls_files:
            nodes.append(ProjectGraphNode(path=cls, file_type='cls'))

        for sty in info.sty_files:
            nodes.append(ProjectGraphNode(path=sty, file_type='sty'))

        return ProjectGraph(
            root=info.main_tex,
            nodes=nodes,
            magic_comments=info.magic_comments,
        )

    def read_fls_file(self, fls_path: Path) -> Dict[str, List[str]]:
        result: Dict[str, List[str]] = {'inputs': [], 'outputs': []}
        if not fls_path.exists():
            return result
        try:
            content = fls_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return result

        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('INPUT '):
                result['inputs'].append(line[6:])
            elif line.startswith('OUTPUT '):
                result['outputs'].append(line[7:])

        return result

    def generate_project_graph_json(self, info: ProjectInfo) -> Dict:
        if not info.project_graph:
            return {}
        graph = info.project_graph
        return {
            'root': str(graph.root) if graph.root else None,
            'magic_comments': graph.magic_comments,
            'nodes': [
                {
                    'path': str(node.path),
                    'file_type': node.file_type,
                    'is_main': node.is_main,
                }
                for node in graph.nodes
            ],
        }
