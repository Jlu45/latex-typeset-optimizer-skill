#!/usr/bin/env python3
"""Configuration loader for LaTeX Typeset Optimizer"""

from pathlib import Path
from typing import Dict, Optional

try:
    import yaml
except ImportError:
    yaml = None

from models import OptimizerConfig, Recipe

DEFAULT_CONFIG = {
    "formatter": "latexindent",
    "fix_level": "safe",
    "compile_policy": "try",
    "write_policy": "copy",
    "build_env": "local",
    "compile_timeout": 300,
    "max_file_size": 104857600,
    "max_log_size": 10485760,
    "enable_shell_escape": False,
    "recipes": {},
    "diagnostics": {
        "output_sarif": True,
        "output_diagnostics": True,
        "output_annotations": False
    },
    "security": {
        "sandbox_mode": True,
        "block_sensitive_paths": True,
        "block_executables": True
    },
    "formatting": {
        "skip_environments": ["minted", "lstlisting", "verbatim"],
        "idempotency_check": True,
        "format_only_changed": False
    }
}


class ConfigLoader:
    def load(self, project_root: Path) -> dict:
        config = dict(DEFAULT_CONFIG)
        config_path = self._find_config_file(project_root)
        if config_path is not None:
            override = self._parse_yaml(config_path)
            if override:
                config = self._deep_merge(config, override)
        return config

    def _deep_merge(self, base: dict, override: dict) -> dict:
        result = dict(base)
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _find_config_file(self, project_root: Path) -> Optional[Path]:
        current = project_root.resolve()
        while True:
            candidate = current / ".latex-optimizer.yaml"
            if candidate.is_file():
                return candidate
            parent = current.parent
            if parent == current:
                break
            current = parent
        return None

    def _parse_yaml(self, path: Path) -> dict:
        if yaml is None:
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if isinstance(data, dict):
                return data
            return {}
        except Exception:
            return {}

    def apply_to_config(self, loaded: dict, config: OptimizerConfig) -> OptimizerConfig:
        if "fix_level" in loaded:
            from models import FixLevel
            try:
                config.fix_level = FixLevel(loaded["fix_level"])
            except ValueError:
                pass
        if "compile_policy" in loaded:
            from models import CompilePolicy
            try:
                config.compile_policy = CompilePolicy(loaded["compile_policy"])
            except ValueError:
                pass
        if "write_policy" in loaded:
            from models import WritePolicy
            try:
                config.write_policy = WritePolicy(loaded["write_policy"])
            except ValueError:
                pass
        if "build_env" in loaded:
            from models import BuildEnvironment
            try:
                config.build_env = BuildEnvironment(loaded["build_env"])
            except ValueError:
                pass
        if "formatter" in loaded:
            pass
        if "compile_timeout" in loaded:
            config.compile_timeout = int(loaded["compile_timeout"])
        if "max_file_size" in loaded:
            config.max_file_size = int(loaded["max_file_size"])
        if "max_log_size" in loaded:
            config.max_log_size = int(loaded["max_log_size"])
        if "enable_shell_escape" in loaded:
            config.enable_shell_escape = bool(loaded["enable_shell_escape"])
        return config

    def get_recipe_definitions(self, loaded: dict) -> Dict[str, Recipe]:
        recipes: Dict[str, Recipe] = {}
        raw = loaded.get("recipes", {})
        if not isinstance(raw, dict):
            return recipes
        for name, definition in raw.items():
            if isinstance(definition, dict):
                tools = definition.get("tools", [])
                if isinstance(tools, list):
                    recipes[name] = Recipe(name=name, tools=tools)
            elif isinstance(definition, list):
                recipes[name] = Recipe(name=name, tools=definition)
        return recipes
