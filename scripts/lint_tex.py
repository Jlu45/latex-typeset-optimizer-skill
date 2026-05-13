#!/usr/bin/env python3
"""LaTeX linter for LaTeX Typeset Optimizer"""

import re
import subprocess
from pathlib import Path
from typing import List, Optional

from models import LintFinding, LintResult


class TexLinter:
    def lint(self, tex_path: Path, linters: List[str]) -> List[LintResult]:
        results = []

        for linter in linters:
            if linter == 'chktex':
                results.append(self._lint_with_chktex(tex_path))
            elif linter == 'lacheck':
                results.append(self._lint_with_lacheck(tex_path))

        if not linters:
            results.append(self._lint_basic(tex_path))

        return results

    def _lint_with_chktex(self, tex_path: Path) -> LintResult:
        cmd = ['chktex', '-q', '-v0', str(tex_path)]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            findings = self._parse_chktex_output(result.stdout, str(tex_path))

            return LintResult(
                linter='chktex',
                file=str(tex_path),
                findings=findings,
                success=True
            )
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return LintResult(
                linter='chktex',
                file=str(tex_path),
                success=False,
                stderr=str(e)
            )

    def _parse_chktex_output(self, output: str,
                             file_path: str) -> List[LintFinding]:
        findings = []

        for line in output.strip().split('\n'):
            if not line.strip():
                continue

            match = re.match(
                r'(?:.*?:)?(\d+):(\d+):\s*(\d+):\s*(.*)',
                line
            )
            if match:
                findings.append(LintFinding(
                    file=file_path,
                    line=int(match.group(1)),
                    column=int(match.group(2)),
                    severity="warning",
                    message=match.group(4).strip(),
                    rule_id=match.group(3)
                ))
            else:
                match2 = re.match(r'(?:.*?:)?(\d+):\s*(.*)', line)
                if match2:
                    findings.append(LintFinding(
                        file=file_path,
                        line=int(match2.group(1)),
                        severity="warning",
                        message=match2.group(2).strip()
                    ))

        return findings

    def _lint_with_lacheck(self, tex_path: Path) -> LintResult:
        cmd = ['lacheck', str(tex_path)]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            findings = self._parse_lacheck_output(result.stdout, str(tex_path))

            return LintResult(
                linter='lacheck',
                file=str(tex_path),
                findings=findings,
                success=True
            )
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return LintResult(
                linter='lacheck',
                file=str(tex_path),
                success=False,
                stderr=str(e)
            )

    def _parse_lacheck_output(self, output: str,
                              file_path: str) -> List[LintFinding]:
        findings = []

        for line in output.strip().split('\n'):
            if not line.strip():
                continue

            match = re.match(r'".*?",\s*line\s*(\d+):\s*(.*)', line)
            if match:
                findings.append(LintFinding(
                    file=file_path,
                    line=int(match.group(1)),
                    severity="warning",
                    message=match.group(2).strip()
                ))

        return findings

    def _lint_basic(self, tex_path: Path) -> LintResult:
        findings = []

        try:
            content = tex_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return LintResult(linter='basic', file=str(tex_path), success=False)

        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            stripped = line.rstrip()

            if stripped != line:
                findings.append(LintFinding(
                    file=str(tex_path),
                    line=i,
                    severity="info",
                    message="Trailing whitespace"
                ))

            if r'\ref{' in line and r'~\ref{' not in line and r'\\ref{' not in line:
                if not line.strip().startswith('%'):
                    findings.append(LintFinding(
                        file=str(tex_path),
                        line=i,
                        severity="info",
                        message="Consider adding non-breaking space before \\ref"
                    ))

            if r'\cite{' in line and r'~\cite{' not in line and r'\\cite{' not in line:
                if not line.strip().startswith('%'):
                    findings.append(LintFinding(
                        file=str(tex_path),
                        line=i,
                        severity="info",
                        message="Consider adding non-breaking space before \\cite"
                    ))

        return LintResult(
            linter='basic',
            file=str(tex_path),
            findings=findings,
            success=True
        )
