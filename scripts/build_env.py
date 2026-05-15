#!/usr/bin/env python3
"""Build environment management for LaTeX Typeset Optimizer"""

import json
import os
import platform
import subprocess

from pathlib import Path
from typing import Optional

from models import EnvironmentInfo, BuildEnvironment, CompileResult, LogAnalysis, Recipe, OptimizerConfig
from parse_log import LogParser


class BuildEnvManager:
    def __init__(self, config: OptimizerConfig):
        self.config = config
        self.log_parser = LogParser()

    def detect_environment(self) -> EnvironmentInfo:
        info = EnvironmentInfo(platform=platform.system())

        try:
            result = subprocess.run(
                ["pdflatex", "--version"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0 and result.stdout:
                first_line = result.stdout.strip().split("\n")[0]
                info.engine_version = first_line.strip()

                for line in result.stdout.split("\n"):
                    if "TeX Live" in line:
                        parts = line.split("TeX Live")
                        if len(parts) > 1:
                            version = parts[1].strip().split()[0].strip("/")
                            info.texlive_version = version
                        break
        except Exception:
            pass

        try:
            result = subprocess.run(
                ["latexmk", "--version"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0 and result.stdout:
                for line in result.stdout.strip().split("\n"):
                    if "latexmk" in line.lower() or any(c.isdigit() for c in line):
                        info.latexmk_version = line.strip()
                        break
        except Exception:
            pass

        try:
            result = subprocess.run(
                ["biber", "--version"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0 and result.stdout:
                for line in result.stdout.strip().split("\n"):
                    if "biber" in line.lower() or any(c.isdigit() for c in line):
                        info.biber_version = line.strip()
                        break
        except Exception:
            pass

        return info

    def prepare_compile_env(self, workspace, project_info) -> dict:
        if self.config.build_env == BuildEnvironment.DOCKER:
            return {
                "DOCKER_IMAGE": self.config.docker_image or "texlive/texlive:latest",
                "SANDBOX_MODE": "1",
            }

        if self.config.build_env == BuildEnvironment.TECTONIC:
            return {
                "TECTONIC_MODE": "1",
                "SANDBOX_MODE": "1",
            }

        return dict(os.environ, SANDBOX_MODE="0")

    def compile_with_docker(self, main_tex: Path, recipe: Recipe, work_dir: Path) -> CompileResult:
        docker_image = self.config.docker_image or "texlive/texlive:latest"

        from recipes import RecipeManager
        manager = RecipeManager()
        commands = manager.build_commands(recipe, main_tex.name, work_dir)

        all_stdout = []
        all_stderr = []
        overall_success = True
        last_return_code = 0

        for cmd in commands:
            docker_cmd = [
                "docker", "run", "--rm",
                "-v", f"{work_dir}:/workspace",
                "-w", "/workspace",
                "--memory=4g",
                "--cpus=2",
                docker_image,
            ] + cmd

            try:
                result = subprocess.run(
                    docker_cmd,
                    capture_output=True,
                    text=True,
                    timeout=600,
                )
                last_return_code = result.returncode
                if result.stdout:
                    all_stdout.append(result.stdout)
                if result.stderr:
                    all_stderr.append(result.stderr)
                if result.returncode != 0:
                    overall_success = False
            except subprocess.TimeoutExpired:
                return CompileResult(
                    success=False,
                    error="Docker compilation timed out (600s)",
                    stdout="\n".join(all_stdout),
                    stderr="\n".join(all_stderr),
                )
            except Exception as e:
                return CompileResult(
                    success=False,
                    error=f"Docker compilation error: {str(e)}",
                    stdout="\n".join(all_stdout),
                    stderr="\n".join(all_stderr),
                )

        log_path = work_dir / main_tex.name.replace(".tex", ".log")
        log_analysis = None
        if log_path.exists():
            log_analysis = self.log_parser.parse(log_path)

        pdf_path = None
        pdf_candidate = work_dir / main_tex.name.replace(".tex", ".pdf")
        if pdf_candidate.exists():
            pdf_path = pdf_candidate

        return CompileResult(
            success=overall_success and (log_analysis is None or log_analysis.no_errors),
            return_code=last_return_code,
            stdout="\n".join(all_stdout),
            stderr="\n".join(all_stderr),
            log_analysis=log_analysis,
            pdf_path=pdf_path,
        )

    def compile_with_tectonic(self, main_tex: Path, work_dir: Path) -> CompileResult:
        try:
            result = subprocess.run(
                ["tectonic", str(main_tex)],
                cwd=str(work_dir),
                capture_output=True,
                text=True,
                timeout=600,
            )

            log_path = work_dir / main_tex.name.replace(".tex", ".log")
            log_analysis = None
            if log_path.exists():
                log_analysis = self.log_parser.parse(log_path)

            pdf_path = None
            pdf_candidate = work_dir / main_tex.name.replace(".tex", ".pdf")
            if pdf_candidate.exists():
                pdf_path = pdf_candidate

            return CompileResult(
                success=result.returncode == 0,
                return_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                log_analysis=log_analysis,
                pdf_path=pdf_path,
            )
        except subprocess.TimeoutExpired:
            return CompileResult(
                success=False,
                error="Tectonic compilation timed out (600s)",
            )
        except Exception as e:
            return CompileResult(
                success=False,
                error=f"Tectonic compilation error: {str(e)}",
            )

    def write_environment_json(self, env_info: EnvironmentInfo, output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "engine_version": env_info.engine_version,
            "latexmk_version": env_info.latexmk_version,
            "biber_version": env_info.biber_version,
            "platform": env_info.platform,
            "texlive_version": env_info.texlive_version,
        }
        output_path = output_dir / "environment.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def check_docker_available(self) -> bool:
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False

    def check_tectonic_available(self) -> bool:
        try:
            result = subprocess.run(
                ["tectonic", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False
