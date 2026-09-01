"""Rename this template: ``uv run python scripts/rename_project.py my_app``."""

from __future__ import annotations

import re
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

OLD_SNAKE = "template_project"
OLD_KEBAB = "template-project"

ROOT = Path(__file__).resolve().parent.parent
SELF = Path(__file__).resolve()
SUFFIXES = {".py", ".toml", ".json", ".md"}
# uv.lock is regenerated rather than rewritten; the rest never hold the old name.
SKIP_DIRS = {
    ".git",
    ".venv",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "htmlcov",
}


def rewritable_files() -> Iterator[Path]:
    """Yield every committed text file that may carry the template's name."""
    for path in ROOT.rglob("*"):
        if path.suffix not in SUFFIXES or not path.is_file():
            continue
        if path.resolve() == SELF or SKIP_DIRS.intersection(path.parts):
            continue
        yield path


def main() -> int:
    """Rewrite the template's name everywhere, then move the package directory."""
    if len(sys.argv) != 2:
        print(__doc__)
        return 1

    new_snake = sys.argv[1]
    if not re.fullmatch(r"[a-z][a-z0-9_]*", new_snake):
        print(f"'{new_snake}' is not a valid Python package name.")
        return 1

    new_kebab = new_snake.replace("_", "-")
    for path in rewritable_files():
        text = path.read_text(encoding="utf-8")
        renamed = text.replace(OLD_SNAKE, new_snake).replace(OLD_KEBAB, new_kebab)
        if renamed != text:
            path.write_text(renamed, encoding="utf-8")
            print(f"rewrote {path.relative_to(ROOT)}")

    subprocess.run(["git", "mv", OLD_SNAKE, new_snake], cwd=ROOT, check=True)
    print(f"moved {OLD_SNAKE}/ -> {new_snake}/")
    print("\nNow run: uv lock && uv run pytest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
