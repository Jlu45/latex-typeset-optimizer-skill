#!/usr/bin/env python3
"""LaTeX compiler for LaTeX Typeset Optimizer"""

import subprocess
from pathlib import Path
from typing import Optional

from models import CompilePolicy, CompileResult, LogAnalysis
from parse_log import LogParser


class CompileError(Exception):
    pass


class TexCompiler:
    def __init__(self, engine: str = "pdflatex",
                 bib_tool: str = "bibtex",
                 latexmkrc_path: Optional[str] = None):
        self.engine = engine
        self.bib_tool = bib_tool
        self.latexmkrc_path = latexmkrc_path
        self.log_parser = LogParser()

    def compile(self, main_tex: Path,
                compile_policy: CompilePolicy) -> CompileResult:
        if compile_policy == CompilePolicy.SKIP:
            return CompileResult(skipped=True)

        if not main_tex or not main_tex.exists():
            return CompileResult(
                success=False,
                error=f"Main tex file not found: {main_tex}"
            )

        work_dir = main_tex.parent
        tex_name = main_tex.name

        try:
            cmd = self._build_command(tex_name)

            result = subprocess.run(
                cmd,
                cwd=str(work_dir),
                capture_output=True,
                text=True,
                timeout=300
            )

            log_path = work_dir / tex_name.replace('.tex', '.log')
            log_analysis = None
            if log_path.exists():
                log_analysis = self.log_parser.parse(log_path)

            pdf_path = None
            pdf_candidate = work_dir / tex_name.replace('.tex', '.pdf')
            if pdf_candidate.exists():
                pdf_path = pdf_candidate

            compile_result = CompileResult(
                success=result.returncode == 0 and (log_analysis is None or log_analysis.no_errors),
                return_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                log_analysis=log_analysis,
                pdf_path=pdf_path
            )

            if compile_policy == CompilePolicy.REQUIRED and not compile_result.success:
                raise CompileError(
                    f"Compilation failed (required policy): {compile_result.stderr[:500]}"
                )

            return compile_result

        except subprocess.TimeoutExpired:
            return CompileResult(
                success=False,
                error="Compilation timed out (5 minutes)"
            )
        except CompileError:
            raise
        except Exception as e:
            return CompileResult(
                success=False,
                error=f"Compilation error: {str(e)}"
            )

    def _build_command(self, tex_name: str) -> list:
        cmd = [
            'latexmk',
            '-pdf',
            f'-pdflatex={self.engine}',
            '-interaction=nonstopmode',
            '-synctex=1',
        ]

        if self.bib_tool == 'biber':
            cmd.append('-bibtex')
        else:
            cmd.append('-bibtex')

        if self.latexmkrc_path:
            cmd.extend(['-r', self.latexmkrc_path])

        cmd.append(tex_name)
        return cmd

    def clean_aux_files(self, work_dir: Path):
        aux_extensions = [
            '.aux', '.log', '.out', '.toc', '.lof', '.lot',
            '.fls', '.fdb_latexmk', '.synctex.gz', '.bbl',
            '.blg', '.nav', '.snm', '.vrb', '.xdv', '.dvi',
            '.ps', '.idx', '.ilg', '.ind', '.ist', '.acn',
            '.acr', '.alg', '.glg', '.glo', '.gls'
        ]

        for ext in aux_extensions:
            for f in work_dir.glob(f'*{ext}'):
                try:
                    f.unlink()
                except OSError:
                    pass
