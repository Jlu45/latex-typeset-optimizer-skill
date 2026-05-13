#!/usr/bin/env python3
"""LaTeX formatter for LaTeX Typeset Optimizer"""

import re
import subprocess
from pathlib import Path
from typing import Optional

from models import FormatResult


class TexFormatter:
    def __init__(self, tool: Optional[str] = None,
                 config_path: Optional[str] = None):
        self.tool = tool
        self.config_path = config_path

    def format(self, tex_path: Path) -> FormatResult:
        if self.tool == 'latexindent':
            return self._format_with_latexindent(tex_path)
        elif self.tool == 'tex-fmt':
            return self._format_with_tex_fmt(tex_path)
        else:
            return self._format_basic(tex_path)

    def _format_with_latexindent(self, tex_path: Path) -> FormatResult:
        cmd = ['latexindent', '-w', '-s']

        if self.config_path:
            cmd.extend(['-l', self.config_path])

        cmd.append(str(tex_path))

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            return FormatResult(
                success=result.returncode == 0,
                output_path=tex_path,
                stderr=result.stderr,
                tool_used='latexindent'
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return self._format_basic(tex_path)

    def _format_with_tex_fmt(self, tex_path: Path) -> FormatResult:
        cmd = ['tex-fmt', str(tex_path)]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                return FormatResult(
                    success=True,
                    output_path=tex_path,
                    tool_used='tex-fmt'
                )
            else:
                return self._format_basic(tex_path)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return self._format_basic(tex_path)

    def _format_basic(self, tex_path: Path) -> FormatResult:
        try:
            content = tex_path.read_text(encoding='utf-8')
        except Exception as e:
            return FormatResult(success=False, stderr=str(e), tool_used='basic')

        original = content

        content = '\n'.join(line.rstrip() for line in content.split('\n'))

        content = re.sub(r'\n{3,}', '\n\n', content)

        if not content.endswith('\n'):
            content += '\n'

        if content != original:
            try:
                tex_path.write_text(content, encoding='utf-8')
            except Exception as e:
                return FormatResult(success=False, stderr=str(e), tool_used='basic')

        return FormatResult(
            success=True,
            output_path=tex_path,
            tool_used='basic'
        )
