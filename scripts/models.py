#!/usr/bin/env python3
"""Shared data types for LaTeX Typeset Optimizer"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class Mode(Enum):
    SINGLE_FILE = "single"
    PROJECT = "project"
    REVIEW_ONLY = "review"
    LOG_REVIEW = "log-review"
    AUTO = "auto"


class Severity(Enum):
    BLOCKING = "blocking"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FixLevel(Enum):
    NONE = "none"
    SAFE = "safe"
    SUGGEST = "suggest"
    AGGRESSIVE = "aggressive"


class CompilePolicy(Enum):
    SKIP = "skip"
    TRY = "try"
    REQUIRED = "required"


class WritePolicy(Enum):
    REPORT_ONLY = "report-only"
    COPY = "copy"
    PATCH_ONLY = "patch-only"


class InputType(Enum):
    SINGLE_TEX = "single-tex"
    ZIP = "zip"
    LOG_ONLY = "log-only"
    DIRECTORY = "directory"
    TEXT = "text"


class BuildEnvironment(Enum):
    LOCAL = "local"
    DOCKER = "docker"
    TECTONIC = "tectonic"


@dataclass
class SecurityNote:
    level: str = "warning"
    category: str = ""
    message: str = ""
    file: Optional[str] = None


@dataclass
class Diagnostic:
    source: str = ""
    rule: Optional[str] = None
    severity: Severity = Severity.INFO
    file: Optional[Path] = None
    line: Optional[int] = None
    column: Optional[int] = None
    message: str = ""
    suggestion: str = ""
    fixable: bool = False
    safe_fix: bool = False


@dataclass
class Recipe:
    name: str = ""
    tools: List[str] = field(default_factory=list)


@dataclass
class EnvironmentInfo:
    engine_version: str = ""
    latexmk_version: str = ""
    biber_version: str = ""
    platform: str = ""
    texlive_version: Optional[str] = None


@dataclass
class ProjectGraphNode:
    path: Path = Path(".")
    node_type: str = ""
    file_type: str = ""
    is_main: bool = False
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ProjectGraph:
    root: Optional[Path] = None
    nodes: List[ProjectGraphNode] = field(default_factory=list)
    magic_comments: Dict[str, str] = field(default_factory=dict)


@dataclass
class OptimizerConfig:
    input: str = ""
    mode: Mode = Mode.AUTO
    output: str = "./output"
    fix_level: FixLevel = FixLevel.SAFE
    compile_policy: CompilePolicy = CompilePolicy.TRY
    write_policy: WritePolicy = WritePolicy.COPY
    engine: Optional[str] = None
    verbose: bool = False
    user_input: str = ""
    build_env: BuildEnvironment = BuildEnvironment.LOCAL
    docker_image: Optional[str] = None
    texlive_version: Optional[str] = None
    recipe_name: Optional[str] = None
    config_file: Optional[str] = None
    max_file_size: int = 104857600
    max_log_size: int = 10485760
    compile_timeout: int = 300
    enable_shell_escape: bool = False


@dataclass
class ProjectWorkspace:
    root: Path = Path(".")
    input_type: InputType = InputType.SINGLE_TEX
    original_path: Optional[str] = None
    _temp_dir: Optional[str] = None
    security_notes: List[SecurityNote] = field(default_factory=list)

    @classmethod
    def create_temp(cls) -> "ProjectWorkspace":
        import tempfile
        temp_dir = tempfile.mkdtemp(prefix="latex_optimizer_")
        workspace = cls(
            root=Path(temp_dir),
            _temp_dir=temp_dir
        )
        return workspace

    def cleanup(self):
        import shutil
        if self._temp_dir and Path(self._temp_dir).exists():
            shutil.rmtree(self._temp_dir, ignore_errors=True)


@dataclass
class TexHeader:
    document_class: str = ""
    packages: List[str] = field(default_factory=list)
    magic_comments: List[str] = field(default_factory=list)
    content: str = ""


@dataclass
class ProjectInfo:
    input_type: str = ""
    main_tex: Optional[Path] = None
    engine_hint: Optional[str] = None
    bib_backend: str = "bibtex"
    uses_cjk: bool = False
    uses_minted: bool = False
    uses_shell_escape: bool = False
    document_class: str = ""
    packages: List[str] = field(default_factory=list)
    tex_files: List[Path] = field(default_factory=list)
    bib_files: List[Path] = field(default_factory=list)
    image_files: List[Path] = field(default_factory=list)
    cls_files: List[Path] = field(default_factory=list)
    sty_files: List[Path] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    magic_comments: Dict[str, str] = field(default_factory=dict)
    arara_directives: List[str] = field(default_factory=list)
    has_latexmkrc: bool = False
    project_graph: Optional[ProjectGraph] = None
    environment_info: Optional[EnvironmentInfo] = None


@dataclass
class Issue:
    severity: Severity
    category: str
    message: str
    file: Optional[Path] = None
    line: Optional[int] = None
    recommendation: str = ""
    auto_fixed: bool = False
    source: str = ""
    rule: Optional[str] = None
    column: Optional[int] = None
    fixable: bool = False
    safe_fix: bool = False


@dataclass
class Diagnostic:
    source: str
    rule: Optional[str] = None
    severity: Severity = Severity.INFO
    file: Optional[Path] = None
    line: Optional[int] = None
    column: Optional[int] = None
    message: str = ""
    suggestion: str = ""
    fixable: bool = False
    safe_fix: bool = False


@dataclass
class IssueSummary:
    compile_status: bool = False
    issue_counts: Dict[Severity, int] = field(default_factory=dict)
    issues: List[Issue] = field(default_factory=list)
    diagnostics: List[Diagnostic] = field(default_factory=list)
    security_notes: List[SecurityNote] = field(default_factory=list)


@dataclass
class FixResult:
    applied: List[str] = field(default_factory=list)
    modified: bool = False
    failed: List[str] = field(default_factory=list)


@dataclass
class LogAnalysis:
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    overfull_boxes: List[str] = field(default_factory=list)
    underfull_boxes: List[str] = field(default_factory=list)
    undefined_refs: List[str] = field(default_factory=list)
    undefined_cites: List[str] = field(default_factory=list)
    no_errors: bool = True
    raw_log: str = ""


@dataclass
class CompileResult:
    success: bool = False
    skipped: bool = False
    return_code: int = 0
    stdout: str = ""
    stderr: str = ""
    error: str = ""
    log_analysis: Optional[LogAnalysis] = None
    pdf_path: Optional[Path] = None
    command_used: List[str] = field(default_factory=list)


@dataclass
class LintFinding:
    file: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None
    severity: str = "warning"
    message: str = ""
    rule_id: Optional[str] = None


@dataclass
class LintResult:
    linter: str
    file: str = ""
    findings: List[LintFinding] = field(default_factory=list)
    success: bool = True
    stderr: str = ""


@dataclass
class FormatResult:
    success: bool
    output_path: Optional[Path] = None
    stderr: str = ""
    tool_used: str = ""
    lines_changed: int = 0
    touched_math: bool = False
    touched_template: bool = False


@dataclass
class ToolSet:
    formatter: Optional[str] = None
    engine: str = "pdflatex"
    bib_tool: str = "bibtex"
    linters: List[str] = field(default_factory=list)
    tectonic_available: bool = False
    docker_available: bool = False


@dataclass
class OptimizationResult:
    project_info: Optional[ProjectInfo] = None
    issue_summary: Optional[IssueSummary] = None
    fix_result: Optional[FixResult] = None
    compile_result: Optional[CompileResult] = None
    output_files: Dict[str, Path] = field(default_factory=dict)
    mode_used: Optional[Mode] = None
    environment_info: Optional[EnvironmentInfo] = None
    security_notes: List[SecurityNote] = field(default_factory=list)
