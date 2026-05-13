#!/usr/bin/env python3
"""Input processor for LaTeX Typeset Optimizer"""

import os
import shutil
import tempfile
import zipfile
from pathlib import Path

from models import ProjectWorkspace, InputType


class IntakeProcessor:
    def process(self, input_path: str) -> ProjectWorkspace:
        workspace = ProjectWorkspace.create_temp()
        workspace.original_path = input_path

        if not input_path or not os.path.exists(input_path):
            if input_path and input_path.strip():
                self._save_text(input_path, workspace)
            return workspace

        if input_path.endswith('.zip'):
            self._unpack_zip(input_path, workspace)
        elif input_path.endswith('.tex'):
            self._copy_tex(input_path, workspace)
        elif input_path.endswith('.log'):
            self._copy_log(input_path, workspace)
        elif os.path.isdir(input_path):
            self._copy_directory(input_path, workspace)
        else:
            self._save_text(input_path, workspace)

        return workspace

    def _unpack_zip(self, zip_path: str, workspace: ProjectWorkspace):
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(workspace.root)

        extracted = list(workspace.root.iterdir())
        if len(extracted) == 1 and extracted[0].is_dir():
            for item in extracted[0].iterdir():
                shutil.move(str(item), str(workspace.root / item.name))
            extracted[0].rmdir()

        workspace.input_type = InputType.ZIP

    def _copy_tex(self, tex_path: str, workspace: ProjectWorkspace):
        src = Path(tex_path)
        dst = workspace.root / src.name
        shutil.copy2(tex_path, dst)

        original_copy = workspace.root / f"{src.stem}_original.tex"
        shutil.copy2(tex_path, original_copy)

        workspace.input_type = InputType.SINGLE_TEX

    def _copy_log(self, log_path: str, workspace: ProjectWorkspace):
        shutil.copy2(log_path, workspace.root / "compile.log")
        workspace.input_type = InputType.LOG_ONLY

    def _copy_directory(self, dir_path: str, workspace: ProjectWorkspace):
        src = Path(dir_path)
        for item in src.iterdir():
            if item.is_file():
                shutil.copy2(str(item), str(workspace.root / item.name))
            elif item.is_dir():
                shutil.copytree(str(item), str(workspace.root / item.name))
        workspace.input_type = InputType.DIRECTORY

    def _save_text(self, text: str, workspace: ProjectWorkspace):
        tex_path = workspace.root / "input.tex"
        tex_path.write_text(text, encoding='utf-8')
        workspace.input_type = InputType.TEXT
