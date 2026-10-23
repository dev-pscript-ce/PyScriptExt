
"""
resolve_path/add_pkg.py

Automatically locate the project root and add it to sys.path.

Author : JP3 Framework
"""

from __future__ import annotations

import inspect
import sys

from collections.abc import Iterable
from pathlib import Path

__all__ = [
    "add_root_project_pkg",
]

# ==========================================================
# Cache
# ==========================================================

_PROJECT_ROOT: Path | None = None

_SKIP_DIRS = {
    "__pycache__",
    ".git",
    ".svn",
    ".hg",
    ".idea",
    ".vscode",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
}


# ==========================================================
# Helpers
# ==========================================================

def _normalize_packages(
    *packages: str | Iterable[str],
) -> tuple[str, ...]:
    """
    Normalize package names.

    Supported:

        add_root_project_pkg("dsl_scan")

        add_root_project_pkg(
            "dsl_scan",
            "modules",
        )

        add_root_project_pkg(
            ["dsl_scan","modules"]
        )

        add_root_project_pkg(
            ("dsl_scan","modules")
        )
    """

    if (
        len(packages) == 1
        and isinstance(packages[0], Iterable)
        and not isinstance(packages[0], (str, bytes))
    ):
        packages = tuple(packages[0])

    packages = tuple(
        str(pkg).strip()
        for pkg in packages
        if str(pkg).strip()
    )

    packages = tuple(dict.fromkeys(packages))

    if not packages:
        raise ValueError(
            "At least one package is required."
        )

    return packages


def _contains_packages(
    root: Path,
    packages: tuple[str, ...],
) -> bool:
    """
    Return True if root contains all packages.
    """

    return all(
        (root / pkg).is_dir()
        and (root / pkg / "__init__.py").is_file()
        for pkg in packages
    )


def _search_down(
    start: Path,
    packages: tuple[str, ...],
) -> Path | None:
    """
    DFS search downward.
    """

    stack = [start]

    while stack:

        current = stack.pop()

        if _contains_packages(current, packages):
            return current.resolve()

        try:

            children = sorted(
                (
                    child
                    for child in current.iterdir()
                    if child.is_dir()
                    and child.name not in _SKIP_DIRS
                ),
                reverse=True,
            )

            stack.extend(children)

        except (
            PermissionError,
            OSError,
        ):
            pass

    return None


# ==========================================================
# Public API
# ==========================================================

def add_root_project_pkg(
    *packages: str | Iterable[str],
) -> Path:
    """
    Automatically locate project root.

    Search order

        1. caller directory

        2. every parent directory

        3. search downward from every parent

    Examples

        ROOT = add_root_project_pkg(
            "dsl_scan"
        )

        ROOT = add_root_project_pkg(
            "dsl_scan",
            "modules",
            "jp_modules",
        )
    """

    global _PROJECT_ROOT

    if _PROJECT_ROOT is not None:
        return _PROJECT_ROOT

    packages = _normalize_packages(*packages)

    # --------------------------------------------------

    caller = Path(
        inspect.currentframe().f_back.f_code.co_filename
    ).resolve()

    start = caller.parent

    # --------------------------------------------------
    # Current + Parents
    # --------------------------------------------------

    current = start

    while True:

        if _contains_packages(
            current,
            packages,
        ):
            root = current.resolve()
            break

        current = current.parent

        if current == current.parent:
            root = None
            break

    # --------------------------------------------------
    # Search downward from every parent
    # --------------------------------------------------

    if root is None:

        current = start

        while True:

            root = _search_down(
                current,
                packages,
            )

            if root:
                break

            current = current.parent

            if current == current.parent:
                break

    # --------------------------------------------------

    if root is None:

        raise RuntimeError(
            "Cannot locate project root.\n"
            f"Required packages: {packages}"
        )

    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    _PROJECT_ROOT = root

    return root

