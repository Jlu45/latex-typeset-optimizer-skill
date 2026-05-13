#!/usr/bin/env python3
"""Issue classifier for LaTeX Typeset Optimizer"""

import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional

from models import LogAnalysis, LintResult, Issue, IssueSummary, Severity


ISSUE_CATEGORIES = {
    'compile-error': {
        'severity': Severity.BLOCKING,
        'description': 'Compilation error'
    },
    'undefined-control-sequence': {
        'severity': Severity.BLOCKING,
        'description': 'Undefined control sequence'
    },
    'missing-package': {
        'severity': Severity.HIGH,
        'description': 'Missing package'
    },
    'undefined-reference': {
        'severity': Severity.HIGH,
        'description': 'Undefined reference'
    },
    'undefined-citation': {
        'severity': Severity.HIGH,
        'description': 'Undefined citation'
    },
    'overfull-box': {
        'severity': Severity.MEDIUM,
        'description': 'Overfull box'
    },
    'underfull-box': {
        'severity': Severity.LOW,
        'description': 'Underfull box'
    },
    'spacing-issue': {
        'severity': Severity.LOW,
        'description': 'Spacing issue'
    },
    'style-issue': {
        'severity': Severity.INFO,
        'description': 'Style issue'
    }
}


class IssueClassifier:
    def classify(self, log_analysis: LogAnalysis,
                 lint_results: List[LintResult]) -> IssueSummary:
        issues = []

        for error in log_analysis.errors:
            issues.append(self._classify_error(error))

        for warning in log_analysis.warnings:
            issues.append(self._classify_warning(warning))

        for box in log_analysis.overfull_boxes:
            line_num = self._extract_line_number(box)
            issues.append(Issue(
                severity=Severity.MEDIUM,
                category='overfull-box',
                message=f'Overfull box: {box}',
                line=line_num,
                recommendation='Consider adjusting line width or using \\sloppy'
            ))

        for box in log_analysis.underfull_boxes:
            line_num = self._extract_line_number(box)
            issues.append(Issue(
                severity=Severity.LOW,
                category='underfull-box',
                message=f'Underfull box: {box}',
                line=line_num,
                recommendation='Consider adjusting spacing or using \\emergencystretch'
            ))

        for ref in log_analysis.undefined_refs:
            issues.append(Issue(
                severity=Severity.HIGH,
                category='undefined-reference',
                message=f'Undefined reference: {ref}',
                recommendation='Check if the label exists or run compilation again'
            ))

        for cite in log_analysis.undefined_cites:
            issues.append(Issue(
                severity=Severity.HIGH,
                category='undefined-citation',
                message=f'Undefined citation: {cite}',
                recommendation='Check bibliography entries or run bibtex/biber'
            ))

        for lint_result in lint_results:
            for finding in lint_result.findings:
                issues.append(Issue(
                    severity=self._map_lint_severity(finding.severity),
                    category=f'lint-{lint_result.linter}',
                    message=finding.message,
                    file=Path(finding.file) if finding.file else None,
                    line=finding.line,
                    recommendation=self._get_lint_recommendation(
                        lint_result.linter, finding
                    )
                ))

        issues.sort(key=lambda i: (i.severity.value, i.line or 0))

        counts = Counter(issue.severity for issue in issues)

        return IssueSummary(
            compile_status=log_analysis.no_errors,
            issue_counts=dict(counts),
            issues=issues
        )

    def _classify_error(self, error: str) -> Issue:
        if 'Undefined control sequence' in error:
            return Issue(
                severity=Severity.BLOCKING,
                category='undefined-control-sequence',
                message=error,
                recommendation='Check if the command is spelled correctly or if a required package is missing'
            )
        elif 'File' in error and 'not found' in error:
            return Issue(
                severity=Severity.BLOCKING,
                category='missing-package',
                message=error,
                recommendation='Check file path or install the missing package'
            )
        elif 'Missing' in error and 'inserted' in error:
            return Issue(
                severity=Severity.BLOCKING,
                category='compile-error',
                message=error,
                recommendation='Check for missing braces, environments, or delimiters'
            )
        else:
            return Issue(
                severity=Severity.BLOCKING,
                category='compile-error',
                message=error,
                recommendation='Review the error message and fix the source'
            )

    def _classify_warning(self, warning: str) -> Issue:
        if 'rerun' in warning.lower():
            return Issue(
                severity=Severity.MEDIUM,
                category='compile-warning',
                message=warning,
                recommendation='Recompile to resolve cross-references'
            )
        elif 'font' in warning.lower():
            return Issue(
                severity=Severity.LOW,
                category='font-warning',
                message=warning,
                recommendation='Check font availability or install missing fonts'
            )
        else:
            return Issue(
                severity=Severity.LOW,
                category='compile-warning',
                message=warning
            )

    def _extract_line_number(self, text: str) -> Optional[int]:
        match = re.search(r'lines? (\d+)', text)
        if match:
            return int(match.group(1))
        return None

    def _map_lint_severity(self, lint_severity: str) -> Severity:
        mapping = {
            'error': Severity.BLOCKING,
            'warning': Severity.MEDIUM,
            'info': Severity.INFO,
            'note': Severity.INFO,
        }
        return mapping.get(lint_severity, Severity.INFO)

    def _get_lint_recommendation(self, linter: str, finding) -> str:
        if linter == 'chktex':
            return f'chktex rule {finding.rule_id}: consider fixing this style issue'
        elif linter == 'lacheck':
            return 'Consider fixing this LaTeX style issue'
        else:
            return 'Review this lint finding'
