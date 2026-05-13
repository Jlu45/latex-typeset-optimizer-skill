#!/usr/bin/env python3
"""Tool availability checker for LaTeX Typeset Optimizer"""

import platform
import subprocess
from typing import Dict, List, Optional

from models import ToolSet


class ToolManager:
    REQUIRED_TOOLS = ['latexmk', 'pdflatex', 'xelatex', 'lualatex']
    OPTIONAL_TOOLS = ['latexindent', 'tex-fmt', 'chktex', 'lacheck']

    def __init__(self):
        self.available_tools: Dict[str, bool] = {}
        self._check_tools()

    def _check_tools(self):
        for tool in self.REQUIRED_TOOLS + self.OPTIONAL_TOOLS:
            self.available_tools[tool] = self._is_tool_available(tool)

    def _is_tool_available(self, tool: str) -> bool:
        try:
            result = subprocess.run(
                [tool, '--version'],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

        try:
            cmd = ['where', tool] if platform.system() == 'Windows' else ['which', tool]
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False

    def select_tools(self, project_info) -> ToolSet:
        tools = ToolSet()

        if self.available_tools.get('latexindent'):
            tools.formatter = 'latexindent'
        elif self.available_tools.get('tex-fmt'):
            tools.formatter = 'tex-fmt'
        else:
            tools.formatter = None

        if hasattr(project_info, 'engine_hint') and project_info.engine_hint:
            tools.engine = project_info.engine_hint
        elif hasattr(project_info, 'uses_cjk') and project_info.uses_cjk:
            tools.engine = 'xelatex'
        else:
            tools.engine = 'pdflatex'

        if not self.available_tools.get(tools.engine):
            for engine in ['pdflatex', 'xelatex', 'lualatex']:
                if self.available_tools.get(engine):
                    tools.engine = engine
                    break

        if hasattr(project_info, 'bib_backend'):
            tools.bib_tool = project_info.bib_backend

        if not self.available_tools.get(tools.bib_tool):
            if tools.bib_tool == 'biber' and not self.available_tools.get('biber'):
                tools.bib_tool = 'bibtex'

        tools.linters = [t for t in ['chktex', 'lacheck']
                        if self.available_tools.get(t)]

        return tools

    def get_status_report(self) -> Dict[str, bool]:
        return dict(self.available_tools)
