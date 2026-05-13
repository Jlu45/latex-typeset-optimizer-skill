#!/usr/bin/env python3
"""Report generator for LaTeX Typeset Optimizer"""

from datetime import datetime
from typing import Dict

from models import Issue, IssueSummary, Severity, FixResult, ProjectInfo, Mode


class ReportGenerator:
    def generate(self, project_info: ProjectInfo,
                 issue_summary: IssueSummary,
                 fix_result: FixResult,
                 mode: Mode) -> str:
        report = []

        report.append("# LaTeX Optimization Report\n")
        report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**Mode**: {mode.value}\n")

        if project_info.main_tex:
            report.append(f"**Main file**: {project_info.main_tex.name}\n")

        if project_info.engine_hint:
            report.append(f"**Engine**: {project_info.engine_hint}\n")

        if project_info.document_class:
            report.append(f"**Document class**: {project_info.document_class}\n")

        report.append("")

        report.append("## Executive Summary\n")
        report.append(self._generate_summary(issue_summary, fix_result))

        report.append("\n## Compilation Status\n")
        if issue_summary.compile_status:
            report.append("**Compilation successful**\n")
        else:
            report.append("**Compilation failed**\n")

        report.append("\n## Issue Statistics\n")
        report.append(self._generate_issue_stats(issue_summary.issue_counts))

        if issue_summary.issues:
            report.append("\n## Detailed Issues\n")
            report.append(self._generate_issue_list(issue_summary.issues))

        if fix_result.applied:
            report.append("\n## Auto Fixes Applied\n")
            report.append(self._generate_fix_list(fix_result.applied))

        if fix_result.failed:
            report.append("\n## Failed Fixes\n")
            report.append(self._generate_failed_list(fix_result.failed))

        report.append("\n## Recommendations\n")
        report.append(self._generate_recommendations(issue_summary))

        if project_info.packages:
            report.append("\n## Packages Used\n")
            report.append(self._generate_package_list(project_info.packages))

        return '\n'.join(report)

    def _generate_summary(self, issue_summary: IssueSummary,
                         fix_result: FixResult) -> str:
        total_issues = sum(issue_summary.issue_counts.values())
        blocking = issue_summary.issue_counts.get(Severity.BLOCKING, 0)
        high = issue_summary.issue_counts.get(Severity.HIGH, 0)

        if blocking > 0:
            summary = f"Found {blocking} blocking issue(s) that require immediate attention. "
        elif high > 0:
            summary = f"Found {high} high-priority issue(s), recommended to address soon. "
        elif total_issues > 0:
            summary = f"Found {total_issues} issue(s), most are low priority. "
        else:
            summary = "No significant issues found, document is in good shape. "

        if fix_result.applied:
            summary += f"\n{len(fix_result.applied)} safe fix(es) were applied automatically."

        return summary + "\n"

    def _generate_issue_stats(self, counts: Dict[Severity, int]) -> str:
        lines = ["| Level | Count |", "|-------|-------|"]

        severity_order = [
            (Severity.BLOCKING, "BLOCKING"),
            (Severity.HIGH, "HIGH"),
            (Severity.MEDIUM, "MEDIUM"),
            (Severity.LOW, "LOW"),
            (Severity.INFO, "INFO"),
        ]

        for severity, label in severity_order:
            count = counts.get(severity, 0)
            lines.append(f"| {label} | {count} |")

        total = sum(counts.values())
        lines.append(f"| **Total** | **{total}** |")

        return '\n'.join(lines)

    def _generate_issue_list(self, issues: list) -> str:
        lines = []

        current_category = None
        for issue in issues:
            if issue.category != current_category:
                current_category = issue.category
                lines.append(f"\n### {current_category}\n")

            location = ""
            if issue.file:
                location += f" ({issue.file.name}"
                if issue.line:
                    location += f":{issue.line}"
                location += ")"

            auto_fix_tag = " [AUTO-FIXED]" if issue.auto_fixed else ""
            lines.append(
                f"- **[{issue.severity.value}]**{auto_fix_tag} {issue.message}{location}"
            )

            if issue.recommendation:
                lines.append(f"  - *Recommendation*: {issue.recommendation}")

        return '\n'.join(lines)

    def _generate_fix_list(self, applied: list) -> str:
        lines = []
        for fix in applied:
            lines.append(f"- {fix}")
        return '\n'.join(lines)

    def _generate_failed_list(self, failed: list) -> str:
        lines = []
        for fail in failed:
            lines.append(f"- {fail}")
        return '\n'.join(lines)

    def _generate_recommendations(self, issue_summary: IssueSummary) -> str:
        lines = []
        blocking = issue_summary.issue_counts.get(Severity.BLOCKING, 0)
        high = issue_summary.issue_counts.get(Severity.HIGH, 0)
        medium = issue_summary.issue_counts.get(Severity.MEDIUM, 0)

        if blocking > 0:
            lines.append("1. **Fix blocking issues first** - These prevent successful compilation.")

        if high > 0:
            lines.append("2. **Address high-priority issues** - Undefined references and citations affect document quality.")

        if medium > 0:
            lines.append("3. **Review overfull boxes** - These may affect the visual layout of your document.")

        if not lines:
            lines.append("- No critical recommendations. Document looks good!")

        return '\n'.join(lines)

    def _generate_package_list(self, packages: list) -> str:
        if not packages:
            return "None detected."

        unique_packages = sorted(set(packages))
        return ", ".join(f"`{pkg}`" for pkg in unique_packages)
