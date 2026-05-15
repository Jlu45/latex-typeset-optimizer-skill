#!/usr/bin/env python3
"""LaTeX formatter for LaTeX Typeset Optimizer"""

import re
import subprocess
from pathlib import Path
from typing import List, Optional

from models import FormatResult


class TexFormatter:
    def __init__(self, tool: Optional[str] = None,
                 config_path: Optional[str] = None,
                 skip_environments: Optional[List[str]] = None,
                 idempotency_check: bool = True):
        self.tool = tool
        self.config_path = config_path
        self.skip_environments = skip_environments if skip_environments is not None else ["minted", "lstlisting", "verbatim"]
        self.idempotency_check = idempotency_check

    def format(self, tex_path: Path) -> FormatResult:
        if self._should_skip_file(tex_path):
            return FormatResult(
                success=True,
                output_path=tex_path,
                tool_used='skip'
            )

        original_content = ""
        try:
            original_content = tex_path.read_text(encoding='utf-8')
        except Exception:
            original_content = ""

        if self.tool == 'latexindent':
            result = self._format_with_latexindent(tex_path)
        elif self.tool == 'tex-fmt':
            result = self._format_with_tex_fmt(tex_path)
        else:
            result = self._format_basic(tex_path)

        formatted_content = ""
        if result.success and result.output_path is not None:
            try:
                formatted_content = result.output_path.read_text(encoding='utf-8')
            except Exception:
                formatted_content = ""

        lines_changed = self._count_lines_changed(original_content, formatted_content)
        touched_math = self._check_touched_math(original_content, formatted_content)
        touched_template = self._check_touched_template(tex_path)

        stderr = result.stderr

        if self.idempotency_check and result.success:
            if not self._check_idempotency(tex_path):
                stderr += "\nWARNING: Idempotency check failed — formatting the file twice produces different output."

        return FormatResult(
            success=result.success,
            output_path=result.output_path,
            stderr=stderr,
            tool_used=result.tool_used,
            lines_changed=lines_changed,
            touched_math=touched_math,
            touched_template=touched_template
        )

    def _should_skip_file(self, tex_path: Path) -> bool:
        suffix = tex_path.suffix.lower()
        if suffix in ('.cls', '.sty'):
            return True
        try:
            content = tex_path.read_text(encoding='utf-8')
        except Exception:
            return False
        for env in self.skip_environments:
            pattern = r'\\begin\{' + re.escape(env) + r'\}'
            if re.search(pattern, content):
                return True
        return False

    def _count_lines_changed(self, original: str, formatted: str) -> int:
        if not original and not formatted:
            return 0
        original_lines = original.splitlines()
        formatted_lines = formatted.splitlines()
        changed = 0
        max_len = max(len(original_lines), len(formatted_lines))
        for i in range(max_len):
            orig_line = original_lines[i] if i < len(original_lines) else None
            fmt_line = formatted_lines[i] if i < len(formatted_lines) else None
            if orig_line != fmt_line:
                changed += 1
        return changed

    def _check_touched_math(self, original: str, formatted: str) -> bool:
        math_patterns = [
            r'(?<!\\)\$.*?(?<!\\)\$',
            r'\\\[.*?\\\]',
            r'\\begin\{align\*?\}',
            r'\\begin\{equation\*?\}',
            r'\\begin\{gather\*?\}',
            r'\\begin\{multline\*?\}',
            r'\\begin\{eqnarray\*?\}',
            r'\\begin\{math\}',
            r'\\begin\{displaymath\}',
        ]
        combined = '|'.join(math_patterns)
        original_matches = set((m.start(), m.group()) for m in re.finditer(combined, original, re.DOTALL))
        formatted_matches = set((m.start(), m.group()) for m in re.finditer(combined, formatted, re.DOTALL))
        return original_matches != formatted_matches

    def _check_touched_template(self, tex_path: Path) -> bool:
        suffix = tex_path.suffix.lower()
        return suffix in ('.cls', '.sty')

    def _check_idempotency(self, tex_path: Path) -> bool:
        try:
            first_pass = tex_path.read_text(encoding='utf-8')
        except Exception:
            return True

        if self.tool == 'latexindent':
            self._format_with_latexindent(tex_path)
        elif self.tool == 'tex-fmt':
            self._format_with_tex_fmt(tex_path)
        else:
            self._format_basic(tex_path)

        try:
            second_pass = tex_path.read_text(encoding='utf-8')
        except Exception:
            return True

        if first_pass == second_pass:
            return True

        if self.tool == 'latexindent':
            self._format_with_latexindent(tex_path)
        elif self.tool == 'tex-fmt':
            self._format_with_tex_fmt(tex_path)
        else:
            self._format_basic(tex_path)

        try:
            third_pass = tex_path.read_text(encoding='utf-8')
        except Exception:
            return False

        return second_pass == third_pass

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
