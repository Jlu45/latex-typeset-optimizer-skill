#!/usr/bin/env python3
"""Output packager for LaTeX Typeset Optimizer"""

import os
import shutil
import zipfile
from pathlib import Path
from typing import Optional


class OutputPackager:
    SKIP_EXTENSIONS = {
        '.aux', '.log', '.out', '.toc', '.lof', '.lot',
        '.fls', '.fdb_latexmk', '.synctex.gz', '.bbl',
        '.blg', '.nav', '.snm', '.vrb', '.xdv', '.dvi',
        '.ps', '.idx', '.ilg', '.ind', '.ist', '.acn',
        '.acr', '.alg', '.glg', '.glo', '.gls', '.ist'
    }

    SKIP_PATTERNS = {'_original.tex'}

    def package(self, workspace_root: Path,
                output_dir: Path,
                project_name: str = "optimized-project") -> Optional[Path]:
        zip_path = output_dir / f"{project_name}.zip"

        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in sorted(workspace_root.rglob('*')):
                    if file_path.is_dir():
                        continue

                    if self._should_skip(file_path):
                        continue

                    arcname = file_path.relative_to(workspace_root)
                    zf.write(file_path, arcname)

            return zip_path

        except Exception as e:
            if zip_path.exists():
                zip_path.unlink()
            return None

    def _should_skip(self, file_path: Path) -> bool:
        if file_path.suffix.lower() in self.SKIP_EXTENSIONS:
            return True

        if file_path.stem in self.SKIP_PATTERNS:
            return True

        name = file_path.name
        if name.startswith('.') and name not in ['.latexmkrc', '.chktexrc']:
            return True

        return False

    def copy_optimized_files(self, workspace_root: Path,
                             output_dir: Path) -> list:
        copied = []

        for file_path in sorted(workspace_root.rglob('*.tex')):
            if file_path.stem.endswith('_original'):
                continue

            rel_path = file_path.relative_to(workspace_root)
            dest = output_dir / rel_path

            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, dest)
            copied.append(dest)

        return copied
