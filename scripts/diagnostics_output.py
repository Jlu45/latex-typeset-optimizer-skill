#!/usr/bin/env python3
"""Unified diagnostics.json output generator for LaTeX Typeset Optimizer"""

import json
from collections import Counter
from pathlib import Path
from typing import Dict, List

from models import Diagnostic, Severity


OUTPUT_VERSION = "0.2.0"


class DiagnosticsGenerator:
    def generate(self, diagnostics: List[Diagnostic]) -> dict:
        by_severity = Counter()
        by_source = Counter()

        serialized = []
        for diag in diagnostics:
            by_severity[diag.severity.name] += 1
            by_source[diag.source] += 1
            serialized.append(self._serialize_diagnostic(diag))

        return {
            "version": OUTPUT_VERSION,
            "diagnostics": serialized,
            "summary": {
                "total": len(diagnostics),
                "by_severity": dict(by_severity),
                "by_source": dict(by_source),
            },
        }

    def generate_json(self, diagnostics: List[Diagnostic]) -> str:
        return json.dumps(self.generate(diagnostics), indent=2)

    def write(self, diagnostics: List[Diagnostic], output_path: Path) -> None:
        output = self.generate(diagnostics)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
            f.write("\n")

    def _serialize_diagnostic(self, diag: Diagnostic) -> dict:
        entry = {
            "source": diag.source,
            "severity": diag.severity.name,
            "message": diag.message,
            "fixable": diag.fixable,
            "safe_fix": diag.safe_fix,
        }

        if diag.rule is not None:
            entry["rule"] = diag.rule

        if diag.file is not None:
            entry["file"] = self._normalize_path(diag.file)

        if diag.line is not None:
            entry["line"] = diag.line

        if diag.column is not None:
            entry["column"] = diag.column

        if diag.suggestion:
            entry["suggestion"] = diag.suggestion

        return entry

    def _normalize_path(self, path: Path) -> str:
        try:
            return path.as_posix()
        except AttributeError:
            return str(path).replace("\\", "/")
