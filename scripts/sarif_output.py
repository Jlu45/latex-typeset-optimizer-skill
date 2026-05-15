#!/usr/bin/env python3
"""SARIF v2.1.0 output generator for GitHub Code Scanning integration"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from models import Diagnostic, Severity


SARIF_SCHEMA = "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"
SARIF_VERSION = "2.1.0"
TOOL_NAME = "latex-typeset-optimizer"
TOOL_VERSION = "0.2.0"
TOOL_URI = "https://github.com/Jlu45/latex-typeset-optimizer"

SEVERITY_MAP: Dict[Severity, str] = {
    Severity.BLOCKING: "error",
    Severity.HIGH: "warning",
    Severity.MEDIUM: "note",
    Severity.LOW: "note",
    Severity.INFO: "none",
}


class SarifGenerator:
    def generate(self, diagnostics: List[Diagnostic]) -> dict:
        rules = self._build_rules(diagnostics)
        results = self._build_results(diagnostics)

        return {
            "$schema": SARIF_SCHEMA,
            "version": SARIF_VERSION,
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": TOOL_NAME,
                            "version": TOOL_VERSION,
                            "informationUri": TOOL_URI,
                            "rules": rules,
                        }
                    },
                    "results": results,
                }
            ],
        }

    def generate_json(self, diagnostics: List[Diagnostic]) -> str:
        return json.dumps(self.generate(diagnostics), indent=2)

    def write(self, diagnostics: List[Diagnostic], output_path: Path) -> None:
        sarif = self.generate(diagnostics)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(sarif, f, indent=2)
            f.write("\n")

    def _build_rules(self, diagnostics: List[Diagnostic]) -> List[dict]:
        seen = {}
        for diag in diagnostics:
            rule_id = diag.rule or self._derive_rule_id(diag)
            if rule_id not in seen:
                seen[rule_id] = {
                    "id": rule_id,
                    "shortDescription": {
                        "text": diag.message or rule_id
                    },
                    "properties": {
                        "tags": [diag.source],
                        "severity": diag.severity.value,
                    },
                }
        return list(seen.values())

    def _build_results(self, diagnostics: List[Diagnostic]) -> List[dict]:
        results = []
        for diag in diagnostics:
            result = self._build_result(diag)
            results.append(result)
        return results

    def _build_result(self, diag: Diagnostic) -> dict:
        rule_id = diag.rule or self._derive_rule_id(diag)
        level = SEVERITY_MAP.get(diag.severity, "none")

        result = {
            "ruleId": rule_id,
            "level": level,
            "message": {
                "text": diag.message,
            },
        }

        if diag.file:
            artifact_location = {
                "uri": self._normalize_path(diag.file),
            }
            location = {
                "physicalLocation": {
                    "artifactLocation": artifact_location,
                },
            }
            if diag.line is not None:
                region = {"startLine": diag.line}
                if diag.column is not None:
                    region["startColumn"] = diag.column
                location["physicalLocation"]["region"] = region
            result["locations"] = [location]

        if diag.suggestion:
            result["fixes"] = [
                {
                    "description": {
                        "text": diag.suggestion,
                    },
                    "artifactChanges": [],
                }
            ]

        result["properties"] = {
            "source": diag.source,
            "fixable": diag.fixable,
            "safeFix": diag.safe_fix,
        }

        return result

    def _derive_rule_id(self, diag: Diagnostic) -> str:
        if diag.rule:
            return diag.rule
        return f"{diag.source}/{diag.severity.value}"

    def _normalize_path(self, path: Path) -> str:
        try:
            return path.as_posix()
        except AttributeError:
            return str(path).replace("\\", "/")
