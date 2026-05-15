#!/usr/bin/env python3
"""Input processor for LaTeX Typeset Optimizer"""

import os
import shutil
import stat
import tempfile
import threading
import zipfile
from pathlib import Path
from typing import List, Optional

from models import ProjectWorkspace, InputType, SecurityNote

SENSITIVE_PATHS = []
_home = os.path.expanduser("~")
if _home != "~":
    SENSITIVE_PATHS.append(Path(_home))
    SENSITIVE_PATHS.append(Path(_home) / ".ssh")
for env_name in (".env", ".bashrc", ".zshrc", ".profile", ".bash_profile"):
    _p = Path(_home) / env_name
    if _p not in SENSITIVE_PATHS:
        SENSITIVE_PATHS.append(_p)

RESTRICTED_EXTENSIONS = {
    ".sh", ".bat", ".cmd", ".ps1", ".exe", ".dll", ".so", ".dylib",
    ".py", ".rb", ".pl", ".lua", ".js",
}
RESTRICTED_NAMES = {
    "Makefile", "makefile", "GNUmakefile",
    "latexmkrc", ".latexmkrc",
    "pre-commit", "post-commit", "pre-push", "post-push",
    "pre-compile", "post-compile",
}

DEFAULT_MAX_FILE_SIZE = 100 * 1024 * 1024
DEFAULT_MAX_LOG_SIZE = 10 * 1024 * 1024
DEFAULT_ZIP_TIMEOUT_SECONDS = 60


class IntakeProcessor:
    def __init__(
        self,
        max_file_size: int = DEFAULT_MAX_FILE_SIZE,
        max_log_size: int = DEFAULT_MAX_LOG_SIZE,
        zip_timeout: int = DEFAULT_ZIP_TIMEOUT_SECONDS,
    ):
        self.max_file_size = max_file_size
        self.max_log_size = max_log_size
        self.zip_timeout = zip_timeout

    def process(self, input_path: str) -> ProjectWorkspace:
        workspace = ProjectWorkspace.create_temp()
        workspace.original_path = input_path

        if not input_path or not os.path.exists(input_path):
            if input_path and input_path.strip():
                self._save_text(input_path, workspace)
            return workspace

        self._check_sensitive_path(input_path, workspace)

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

        self._scan_symlinks(workspace)
        self._scan_restricted_files(workspace)

        return workspace

    def _check_sensitive_path(self, path_str: str, workspace: ProjectWorkspace):
        try:
            resolved = Path(path_str).resolve()
        except (OSError, ValueError):
            return
        for sensitive in SENSITIVE_PATHS:
            try:
                resolved.relative_to(sensitive)
                workspace.security_notes.append(SecurityNote(
                    level="error",
                    category="sensitive_path",
                    message=f"Input path resolves inside sensitive directory: {sensitive}",
                    file=path_str,
                ))
            except ValueError:
                continue

    def _validate_zip_entry(self, entry: zipfile.ZipInfo, workspace: ProjectWorkspace) -> bool:
        name = entry.filename
        if os.path.isabs(name):
            workspace.security_notes.append(SecurityNote(
                level="error",
                category="zip_slip",
                message=f"Zip entry has absolute path: {name}",
                file=name,
            ))
            return False
        if ".." in Path(name).parts:
            workspace.security_notes.append(SecurityNote(
                level="error",
                category="zip_slip",
                message=f"Zip entry contains '..' component: {name}",
                file=name,
            ))
            return False
        return True

    def _unpack_zip(self, zip_path: str, workspace: ProjectWorkspace):
        result_holder = [None]
        error_holder = [None]

        def _extract():
            try:
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    for entry in zf.infolist():
                        if not self._validate_zip_entry(entry, workspace):
                            continue
                        if entry.file_size > self.max_file_size:
                            workspace.security_notes.append(SecurityNote(
                                level="error",
                                category="max_file_size",
                                message=f"Zip entry exceeds max file size ({self.max_file_size} bytes): {entry.filename}",
                                file=entry.filename,
                            ))
                            continue
                        extracted_path = (workspace.root / entry.filename).resolve()
                        try:
                            workspace.root.resolve().relative_to(extracted_path)
                        except ValueError:
                            pass
                        if not str(extracted_path).startswith(str(workspace.root.resolve())):
                            workspace.security_notes.append(SecurityNote(
                                level="error",
                                category="zip_slip",
                                message=f"Zip entry resolves outside workspace: {entry.filename}",
                                file=entry.filename,
                            ))
                            continue
                        zf.extract(entry, workspace.root)
                result_holder[0] = True
            except Exception as e:
                error_holder[0] = e

        thread = threading.Thread(target=_extract)
        thread.start()
        thread.join(timeout=self.zip_timeout)

        if thread.is_alive():
            workspace.security_notes.append(SecurityNote(
                level="error",
                category="zip_timeout",
                message=f"Zip extraction timed out after {self.zip_timeout} seconds",
                file=zip_path,
            ))
            raise RuntimeError(f"Zip extraction timed out after {self.zip_timeout} seconds")

        if error_holder[0] is not None:
            raise error_holder[0]

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
        self._make_readonly(original_copy)

        workspace.input_type = InputType.SINGLE_TEX

    def _copy_log(self, log_path: str, workspace: ProjectWorkspace):
        log_size = os.path.getsize(log_path)
        if log_size > self.max_log_size:
            workspace.security_notes.append(SecurityNote(
                level="warning",
                category="max_log_size",
                message=f"Log file exceeds max log size ({self.max_log_size} bytes): {log_size} bytes",
                file=log_path,
            ))
        shutil.copy2(log_path, workspace.root / "compile.log")
        workspace.input_type = InputType.LOG_ONLY

    def _copy_directory(self, dir_path: str, workspace: ProjectWorkspace):
        src = Path(dir_path)
        for item in src.iterdir():
            if item.is_file():
                file_size = item.stat().st_size
                if file_size > self.max_file_size:
                    workspace.security_notes.append(SecurityNote(
                        level="warning",
                        category="max_file_size",
                        message=f"File exceeds max file size ({self.max_file_size} bytes): {item.name}",
                        file=str(item),
                    ))
                    continue
                shutil.copy2(str(item), str(workspace.root / item.name))
            elif item.is_dir():
                shutil.copytree(str(item), str(workspace.root / item.name))
        workspace.input_type = InputType.DIRECTORY

    def _save_text(self, text: str, workspace: ProjectWorkspace):
        tex_path = workspace.root / "input.tex"
        tex_path.write_text(text, encoding='utf-8')
        workspace.input_type = InputType.TEXT

    def _make_readonly(self, path: Path):
        try:
            current = path.stat().st_mode
            path.chmod(current & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
        except OSError:
            pass

    def _scan_symlinks(self, workspace: ProjectWorkspace):
        for root, dirs, files in os.walk(workspace.root, followlinks=False):
            for name in files + dirs:
                full = os.path.join(root, name)
                if os.path.islink(full):
                    workspace.security_notes.append(SecurityNote(
                        level="warning",
                        category="symlink",
                        message=f"Symbolic link found and removed: {os.path.relpath(full, workspace.root)}",
                        file=os.path.relpath(full, workspace.root),
                    ))
                    try:
                        os.remove(full)
                    except OSError:
                        try:
                            shutil.rmtree(full)
                        except OSError:
                            pass

    def _scan_restricted_files(self, workspace: ProjectWorkspace):
        for root, dirs, files in os.walk(workspace.root):
            for name in files:
                full = os.path.join(root, name)
                rel = os.path.relpath(full, workspace.root)
                stem, ext = os.path.splitext(name)
                is_restricted = False

                if ext.lower() in RESTRICTED_EXTENSIONS:
                    is_restricted = True
                if name in RESTRICTED_NAMES:
                    is_restricted = True

                if is_restricted:
                    workspace.security_notes.append(SecurityNote(
                        level="warning",
                        category="restricted_file",
                        message=f"Restricted file detected in workspace: {name}",
                        file=rel,
                    ))
                    original_copy = Path(full).with_suffix(ext + ".restricted")
                    try:
                        shutil.copy2(full, original_copy)
                        self._make_readonly(original_copy)
                    except OSError:
                        pass
