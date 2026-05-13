#!/usr/bin/env python3
"""LaTeX Typeset Optimizer - Main Entry Point"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, Optional

from models import (
    Mode, Severity, FixLevel, CompilePolicy, WritePolicy,
    OptimizerConfig, OptimizationResult, ProjectWorkspace,
    ProjectInfo, ToolSet, IssueSummary, FixResult, CompileResult
)
from intake import IntakeProcessor
from detect_project import ProjectDetector
from tool_check import ToolManager
from format_tex import TexFormatter
from lint_tex import TexLinter
from compile_tex import TexCompiler
from parse_log import LogParser, LogAnalysis
from classify_issues import IssueClassifier
from apply_safe_fixes import SafeFixer
from diff_utils import DiffGenerator
from package_output import OutputPackager
from make_report import ReportGenerator


MODE_MAPPING = {
    "single": {
        "fix-level": "safe",
        "compile-policy": "try",
        "write-policy": "copy"
    },
    "project": {
        "fix-level": "safe",
        "compile-policy": "try",
        "write-policy": "copy"
    },
    "review": {
        "fix-level": "none",
        "compile-policy": "try",
        "write-policy": "report-only"
    }
}


class ModeRouter:
    REVIEW_ONLY_TRIGGERS = [
        "只检查", "不要修改", "不要改文件", "只给报告",
        "review only", "audit only", "no edits", "no changes",
        "只审查", "仅检查", "不要动文件"
    ]

    PROJECT_TRIGGERS = [
        "overleaf", "项目", "project", "论文", "thesis",
        "dissertation", "投稿", "submission", "arxiv"
    ]

    def detect_mode(self, config: OptimizerConfig) -> Mode:
        user_input = config.user_input.lower()
        input_path = config.input

        if any(trigger in user_input for trigger in self.REVIEW_ONLY_TRIGGERS):
            return Mode.REVIEW_ONLY

        if input_path.endswith('.log'):
            return Mode.LOG_REVIEW

        if input_path.endswith('.zip'):
            return Mode.PROJECT

        if input_path.endswith('.tex'):
            if self._is_part_of_project(input_path):
                return Mode.PROJECT
            return Mode.SINGLE_FILE

        if os.path.isdir(input_path):
            return Mode.PROJECT

        if any(trigger in user_input for trigger in self.PROJECT_TRIGGERS):
            return Mode.PROJECT

        return Mode.SINGLE_FILE

    def _is_part_of_project(self, tex_path: str) -> bool:
        parent_dir = Path(tex_path).parent
        indicators = ['figures', 'sections', 'chapters', 'bib', 'images']
        return any((parent_dir / ind).exists() for ind in indicators)


class LatexOptimizer:
    def __init__(self, config: OptimizerConfig):
        self.config = config
        self.mode_router = ModeRouter()
        self.intake = IntakeProcessor()
        self.detector = ProjectDetector()
        self.tool_manager = ToolManager()
        self.formatter = None
        self.linter = TexLinter()
        self.compiler = None
        self.log_parser = LogParser()
        self.classifier = IssueClassifier()
        self.fixer = SafeFixer(config.fix_level)
        self.diff_gen = DiffGenerator()
        self.reporter = ReportGenerator()
        self.packager = OutputPackager()

    def run(self) -> OptimizationResult:
        result = OptimizationResult()

        mode = self.mode_router.detect_mode(self.config)
        result.mode_used = mode

        if self.config.verbose:
            print(f"[INFO] Detected mode: {mode.value}")

        workspace = self.intake.process(self.config.input)
        if self.config.verbose:
            print(f"[INFO] Workspace: {workspace.root}")

        project_info = self.detector.analyze(workspace)
        result.project_info = project_info

        tools = self.tool_manager.select_tools(project_info)

        if self.config.engine:
            tools.engine = self.config.engine

        self.formatter = TexFormatter(
            tool=tools.formatter,
            config_path=self._get_config_path('latexindent-default.yaml')
        )
        self.compiler = TexCompiler(
            engine=tools.engine,
            bib_tool=tools.bib_tool,
            latexmkrc_path=self._get_config_path('latexmkrc-default')
        )

        if mode == Mode.SINGLE_FILE:
            result = self._optimize_single(workspace, project_info, tools, result)
        elif mode == Mode.PROJECT:
            result = self._optimize_project(workspace, project_info, tools, result)
        elif mode == Mode.REVIEW_ONLY:
            result = self._review_only(workspace, project_info, tools, result)
        elif mode == Mode.LOG_REVIEW:
            result = self._review_log(workspace, result)

        self._generate_outputs(result, workspace, mode)

        return result

    def _optimize_single(self, workspace, project_info, tools, result):
        tex_path = project_info.main_tex
        if not tex_path or not tex_path.exists():
            return result

        format_result = self.formatter.format(tex_path)
        if self.config.verbose:
            print(f"[INFO] Format: {'success' if format_result.success else 'failed'}")

        lint_results = self.linter.lint(tex_path, tools.linters)

        compile_result = self.compiler.compile(
            tex_path, self.config.compile_policy
        )
        result.compile_result = compile_result

        log_analysis = LogAnalysis()
        if compile_result and compile_result.log_analysis:
            log_analysis = compile_result.log_analysis
        elif tex_path.with_suffix('.log').exists():
            log_analysis = self.log_parser.parse(tex_path.with_suffix('.log'))

        issue_summary = self.classifier.classify(log_analysis, lint_results)
        result.issue_summary = issue_summary

        fix_result = self.fixer.apply_fixes(tex_path, issue_summary.issues)
        result.fix_result = fix_result

        return result

    def _optimize_project(self, workspace, project_info, tools, result):
        all_lint_results = []

        for tex_file in project_info.tex_files:
            self.formatter.format(tex_file)
            lint_results = self.linter.lint(tex_file, tools.linters)
            all_lint_results.extend(lint_results)

        compile_result = None
        log_analysis = LogAnalysis()

        if project_info.main_tex and project_info.main_tex.exists():
            compile_result = self.compiler.compile(
                project_info.main_tex, self.config.compile_policy
            )
            result.compile_result = compile_result

            if compile_result and compile_result.log_analysis:
                log_analysis = compile_result.log_analysis
            elif project_info.main_tex.with_suffix('.log').exists():
                log_analysis = self.log_parser.parse(
                    project_info.main_tex.with_suffix('.log')
                )

        issue_summary = self.classifier.classify(log_analysis, all_lint_results)
        result.issue_summary = issue_summary

        all_fix_results = []
        for tex_file in project_info.tex_files:
            fix_result = self.fixer.apply_fixes(tex_file, issue_summary.issues)
            all_fix_results.append(fix_result)

        if all_fix_results:
            merged_applied = []
            merged_failed = []
            modified = False
            for fr in all_fix_results:
                merged_applied.extend(fr.applied)
                merged_failed.extend(fr.failed)
                if fr.modified:
                    modified = True
            result.fix_result = FixResult(
                applied=list(dict.fromkeys(merged_applied)),
                modified=modified,
                failed=list(dict.fromkeys(merged_failed))
            )

        return result

    def _review_only(self, workspace, project_info, tools, result):
        all_lint_results = []

        for tex_file in project_info.tex_files:
            lint_results = self.linter.lint(tex_file, tools.linters)
            all_lint_results.extend(lint_results)

        log_analysis = LogAnalysis()
        if project_info.main_tex and project_info.main_tex.exists():
            compile_result = self.compiler.compile(
                project_info.main_tex, self.config.compile_policy
            )
            result.compile_result = compile_result

            if compile_result and compile_result.log_analysis:
                log_analysis = compile_result.log_analysis
            elif project_info.main_tex.with_suffix('.log').exists():
                log_analysis = self.log_parser.parse(
                    project_info.main_tex.with_suffix('.log')
                )

        issue_summary = self.classifier.classify(log_analysis, all_lint_results)
        result.issue_summary = issue_summary

        result.fix_result = FixResult(applied=[], modified=False, failed=[])

        return result

    def _review_log(self, workspace, result):
        log_files = list(workspace.root.glob('*.log'))
        if not log_files:
            return result

        log_analysis = self.log_parser.parse(log_files[0])
        issue_summary = self.classifier.classify(log_analysis, [])
        result.issue_summary = issue_summary
        result.fix_result = FixResult(applied=[], modified=False, failed=[])

        project_info = ProjectInfo()
        project_info.main_tex = log_files[0]
        result.project_info = project_info

        return result

    def _generate_outputs(self, result, workspace, mode):
        output_dir = Path(self.config.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        if result.project_info and result.project_info.main_tex:
            report = self.reporter.generate(
                result.project_info,
                result.issue_summary or IssueSummary(),
                result.fix_result or FixResult(),
                mode
            )
            report_path = output_dir / "report.md"
            report_path.write_text(report, encoding='utf-8')
            result.output_files['report'] = report_path

            if result.issue_summary:
                summary_data = self._issue_summary_to_dict(result.issue_summary)
                summary_path = output_dir / "issue-summary.json"
                summary_path.write_text(
                    json.dumps(summary_data, ensure_ascii=False, indent=2),
                    encoding='utf-8'
                )
                result.output_files['issue-summary'] = summary_path

        if mode == Mode.SINGLE_FILE and result.project_info and result.project_info.main_tex:
            tex_path = result.project_info.main_tex
            if tex_path.exists():
                optimized_path = output_dir / "optimized.tex"
                shutil.copy2(tex_path, optimized_path)
                result.output_files['optimized'] = optimized_path

                original_path = workspace.root / f"{tex_path.stem}_original.tex"
                if not original_path.exists():
                    original_path = workspace.root / tex_path.name

                diff = self.diff_gen.generate_diff(
                    str(original_path), str(tex_path)
                )
                if diff:
                    diff_path = output_dir / "patch.diff"
                    diff_path.write_text(diff, encoding='utf-8')
                    result.output_files['diff'] = diff_path

        elif mode == Mode.PROJECT:
            zip_path = self.packager.package(workspace.root, output_dir)
            if zip_path:
                result.output_files['optimized-project'] = zip_path

            if result.project_info and result.project_info.main_tex:
                diff = self.diff_gen.generate_project_diff(workspace.root)
                if diff:
                    diff_path = output_dir / "patch.diff"
                    diff_path.write_text(diff, encoding='utf-8')
                    result.output_files['diff'] = diff_path

        if self.config.verbose:
            print(f"[INFO] Output files:")
            for name, path in result.output_files.items():
                print(f"  {name}: {path}")

    def _issue_summary_to_dict(self, summary: IssueSummary) -> dict:
        return {
            "compile_status": summary.compile_status,
            "issue_counts": {
                s.value: count for s, count in summary.issue_counts.items()
            },
            "issues": [
                {
                    "severity": issue.severity.value,
                    "category": issue.category,
                    "message": issue.message,
                    "file": str(issue.file) if issue.file else None,
                    "line": issue.line,
                    "recommendation": issue.recommendation,
                    "auto_fixed": issue.auto_fixed
                }
                for issue in summary.issues
            ]
        }

    def _get_config_path(self, filename: str) -> Optional[str]:
        config_dir = Path(__file__).parent.parent / "configs" / filename
        if config_dir.exists():
            return str(config_dir)
        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="LaTeX Typeset Optimizer - Multi-mode LaTeX optimization tool"
    )
    parser.add_argument(
        "--input", required=True,
        help="Input path (.tex / .zip / .log / directory)"
    )
    parser.add_argument(
        "--mode", default="auto",
        choices=["auto", "single", "project", "review", "log-review"],
        help="Run mode (default: auto)"
    )
    parser.add_argument(
        "--output", default="./output",
        help="Output directory (default: ./output)"
    )
    parser.add_argument(
        "--fix-level", default="safe",
        choices=["none", "safe", "suggest", "aggressive"],
        help="Fix level (default: safe)"
    )
    parser.add_argument(
        "--compile-policy", default="try",
        choices=["skip", "try", "required"],
        help="Compile policy (default: try)"
    )
    parser.add_argument(
        "--write-policy", default="copy",
        choices=["report-only", "copy", "patch-only"],
        help="Write policy (default: copy)"
    )
    parser.add_argument(
        "--engine", default=None,
        choices=["pdflatex", "xelatex", "lualatex"],
        help="Force specific engine"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--user-input", default="",
        help="Original user input for intent detection"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    mode_map = {
        "auto": Mode.AUTO,
        "single": Mode.SINGLE_FILE,
        "project": Mode.PROJECT,
        "review": Mode.REVIEW_ONLY,
        "log-review": Mode.LOG_REVIEW
    }

    fix_level_map = {
        "none": FixLevel.NONE,
        "safe": FixLevel.SAFE,
        "suggest": FixLevel.SUGGEST,
        "aggressive": FixLevel.AGGRESSIVE
    }

    compile_policy_map = {
        "skip": CompilePolicy.SKIP,
        "try": CompilePolicy.TRY,
        "required": CompilePolicy.REQUIRED
    }

    write_policy_map = {
        "report-only": WritePolicy.REPORT_ONLY,
        "copy": WritePolicy.COPY,
        "patch-only": WritePolicy.PATCH_ONLY
    }

    config = OptimizerConfig(
        input=args.input,
        mode=mode_map[args.mode],
        output=args.output,
        fix_level=fix_level_map[args.fix_level],
        compile_policy=compile_policy_map[args.compile_policy],
        write_policy=write_policy_map[args.write_policy],
        engine=args.engine,
        verbose=args.verbose,
        user_input=args.user_input
    )

    optimizer = LatexOptimizer(config)
    result = optimizer.run()

    if result.issue_summary:
        total = sum(result.issue_summary.issue_counts.values())
        blocking = result.issue_summary.issue_counts.get(Severity.BLOCKING, 0)
        print(f"\n{'='*60}")
        print(f"Optimization complete. Mode: {result.mode_used.value}")
        print(f"Total issues: {total}, Blocking: {blocking}")
        if result.output_files:
            print(f"Output files:")
            for name, path in result.output_files.items():
                print(f"  {name}: {path}")
        print(f"{'='*60}")

    return 0 if not result.issue_summary or result.issue_summary.compile_status else 1


if __name__ == "__main__":
    sys.exit(main())
