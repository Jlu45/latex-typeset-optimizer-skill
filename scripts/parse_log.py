#!/usr/bin/env python3
"""LaTeX compilation log parser for LaTeX Typeset Optimizer"""

import re
from pathlib import Path

from models import LogAnalysis


class LogParser:
    def parse(self, log_path: Path) -> LogAnalysis:
        analysis = LogAnalysis()

        try:
            content = log_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return analysis

        analysis.raw_log = content

        analysis.errors = self._parse_errors(content)
        analysis.warnings = self._parse_warnings(content)
        analysis.overfull_boxes = self._parse_overfull(content)
        analysis.underfull_boxes = self._parse_underfull(content)
        analysis.undefined_refs = self._parse_undefined_refs(content)
        analysis.undefined_cites = self._parse_undefined_cites(content)
        analysis.no_errors = len(analysis.errors) == 0

        return analysis

    def _parse_errors(self, content: str) -> list:
        errors = []

        error_pattern = r'^! (.+?)(?=\n\n|\nl\.\n|\n<to be read again>|\n<*>)'
        for match in re.finditer(error_pattern, content, re.MULTILINE | re.DOTALL):
            error_text = match.group(1).strip()
            if error_text and error_text not in errors:
                errors.append(error_text)

        return errors

    def _parse_warnings(self, content: str) -> list:
        warnings = []

        warning_patterns = [
            r'LaTeX Warning: (.+?)(?=\n\n|\nLaTeX Warning:|\n\(|\Z)',
            r'Package (\w+) Warning: (.+?)(?=\n\n|\nPackage|\Z)',
        ]

        for pattern in warning_patterns:
            for match in re.finditer(pattern, content, re.DOTALL):
                warning_text = match.group(0).strip()
                if warning_text and warning_text not in warnings:
                    warnings.append(warning_text)

        return warnings

    def _parse_overfull(self, content: str) -> list:
        overfull = []

        patterns = [
            r'Overfull \\hbox \(([^)]+)\) (?:in paragraph|detected) at lines? (\d+)',
            r'Overfull \\vbox \(([^)]+)\) (?:in paragraph|detected) at lines? (\d+)',
            r'Overfull \\hbox \(([^)]+)\) (?:in paragraph|detected) at line (\d+)',
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, content):
                entry = f"line {match.group(2)}: {match.group(1)}"
                if entry not in overfull:
                    overfull.append(entry)

        simple_pattern = r'Overfull \\[vh]box .+?(?=\n\n|\nOverfull|\nUnderfull|\Z)'
        for match in re.finditer(simple_pattern, content, re.DOTALL):
            text = match.group(0).strip()
            if text and text not in overfull:
                overfull.append(text)

        return overfull

    def _parse_underfull(self, content: str) -> list:
        underfull = []

        patterns = [
            r'Underfull \\hbox .+? at lines? (\d+)',
            r'Underfull \\vbox .+? at lines? (\d+)',
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, content):
                entry = f"line {match.group(1)}"
                if entry not in underfull:
                    underfull.append(entry)

        simple_pattern = r'Underfull \\[vh]box .+?(?=\n\n|\nOverfull|\nUnderfull|\Z)'
        for match in re.finditer(simple_pattern, content, re.DOTALL):
            text = match.group(0).strip()
            if text and text not in underfull:
                underfull.append(text)

        return underfull

    def _parse_undefined_refs(self, content: str) -> list:
        refs = []

        patterns = [
            r"Reference `([^']+)' on page \d+ undefined",
            r"Reference `([^']+)' undefined",
            r"Reference `([^']+)' on page \d+",
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, content):
                ref = match.group(1)
                if ref not in refs:
                    refs.append(ref)

        return refs

    def _parse_undefined_cites(self, content: str) -> list:
        cites = []

        patterns = [
            r"Citation `([^']+)' on page \d+ undefined",
            r"Citation `([^']+)' undefined",
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, content):
                cite = match.group(1)
                if cite not in cites:
                    cites.append(cite)

        return cites
