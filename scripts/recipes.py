#!/usr/bin/env python3
"""Build recipes for LaTeX Typeset Optimizer"""

from pathlib import Path
from typing import List, Optional

from models import Recipe, ProjectInfo

BUILT_IN_RECIPES = {
    "latexmk-pdf": Recipe(
        name="latexmk-pdf",
        tools=["latexmk -pdf -file-line-error -halt-on-error -interaction=nonstopmode"],
    ),
    "latexmk-xelatex": Recipe(
        name="latexmk-xelatex",
        tools=["latexmk -pdf -pdflatex=xelatex -file-line-error -halt-on-error -interaction=nonstopmode"],
    ),
    "latexmk-lualatex": Recipe(
        name="latexmk-lualatex",
        tools=["latexmk -pdf -pdflatex=lualatex -file-line-error -halt-on-error -interaction=nonstopmode"],
    ),
    "pdflatex-bibtex": Recipe(
        name="pdflatex-bibtex",
        tools=["pdflatex", "bibtex", "pdflatex", "pdflatex"],
    ),
    "pdflatex-biber": Recipe(
        name="pdflatex-biber",
        tools=["pdflatex", "biber", "pdflatex", "pdflatex"],
    ),
    "tectonic": Recipe(
        name="tectonic",
        tools=["tectonic"],
    ),
}


class RecipeManager:
    def __init__(self, config=None):
        self.recipes = dict(BUILT_IN_RECIPES)
        self.config = config
        if config and hasattr(config, "config_file") and config.config_file:
            config_path = Path(config.config_file)
            if config_path.exists():
                self.load_from_yaml(str(config_path))

    def load_from_yaml(self, yaml_path: str):
        try:
            import yaml
        except ImportError:
            return

        path = Path(yaml_path)
        if not path.exists():
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception:
            return

        if not data or "recipes" not in data:
            return

        for name, recipe_data in data["recipes"].items():
            if isinstance(recipe_data, dict) and "tools" in recipe_data:
                self.recipes[name] = Recipe(
                    name=name,
                    tools=recipe_data["tools"],
                )

    def select_recipe(self, project_info: ProjectInfo) -> Recipe:
        if project_info.arara_directives:
            return Recipe(name="arara", tools=["arara"])

        if project_info.has_latexmkrc:
            if project_info.engine_hint == "xelatex":
                return self.recipes["latexmk-xelatex"]
            if project_info.engine_hint == "lualatex":
                return self.recipes["latexmk-lualatex"]
            return self.recipes["latexmk-pdf"]

        if project_info.engine_hint == "xelatex":
            return self.recipes["latexmk-xelatex"]
        if project_info.engine_hint == "lualatex":
            return self.recipes["latexmk-lualatex"]
        if project_info.bib_backend == "biber":
            return self.recipes["pdflatex-biber"]

        return self.recipes["latexmk-pdf"]

    def get_recipe(self, name: str) -> Optional[Recipe]:
        return self.recipes.get(name)

    def list_recipes(self) -> List[str]:
        return list(self.recipes.keys())

    def build_commands(self, recipe: Recipe, tex_name: str, work_dir: Path, latexmkrc_path: Optional[str] = None) -> List[List[str]]:
        commands = []
        tex_stem = tex_name.replace(".tex", "")

        for tool in recipe.tools:
            if tool.startswith("latexmk"):
                cmd = tool.split()
                if latexmkrc_path:
                    cmd.extend(["-r", latexmkrc_path])
                cmd.append(tex_name)
                commands.append(cmd)
            elif tool in ("pdflatex", "xelatex", "lualatex"):
                cmd = [
                    tool,
                    "-interaction=nonstopmode",
                    "-file-line-error",
                    "-halt-on-error",
                    tex_name,
                ]
                commands.append(cmd)
            elif tool == "bibtex":
                commands.append(["bibtex", tex_stem])
            elif tool == "biber":
                commands.append(["biber", tex_stem])
            elif tool == "tectonic":
                commands.append(["tectonic", tex_name])
            elif tool == "arara":
                commands.append(["arara", tex_name])
            else:
                cmd = tool.split()
                cmd.append(tex_name)
                commands.append(cmd)

        return commands
