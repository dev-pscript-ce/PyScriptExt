from __future__ import annotations

import inspect

from pathlib import Path

__all__ = [
    "find_file",
]

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

# Cache
_FILE_CACHE: dict[tuple[str, str | None], Path] = {}


def _search_down(
    start: Path,
    filename: str,
) -> Path | None:
    """
    DFS search.
    """

    stack = [start]

    while stack:

        current = stack.pop()

        candidate = current / filename

        if candidate.is_file():
            return candidate.resolve()

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

        except (PermissionError, OSError):
            pass

    return None


def find_file(
    filename: str | Path,
    *,
    root: str | Path | None = None,
    start: str | Path | None = None,
) -> Path:
    """
    Locate a file.

    Search order
    ------------

    1. Absolute filename.

    2. root / filename

    3. caller directory

    4. parent directories

    5. recursive search downward from every parent

    Parameters
    ----------
    filename
        File name or path.

    root
        Project root.

    start
        Search start directory.
        Default = caller directory.
    """

    filename = Path(filename)

    # --------------------------------------------------
    # absolute path
    # --------------------------------------------------

    if filename.is_absolute():

        if filename.is_file():
            return filename.resolve()

        raise FileNotFoundError(filename)

    # --------------------------------------------------
    # cache
    # --------------------------------------------------

    cache_key = (
        filename.as_posix(),
        None if root is None else str(Path(root).resolve()),
    )

    if cache_key in _FILE_CACHE:
        return _FILE_CACHE[cache_key]

    # --------------------------------------------------
    # project root
    # --------------------------------------------------

    if root is not None:

        root = Path(root).resolve()

        candidate = root / filename

        if candidate.is_file():

            candidate = candidate.resolve()

            _FILE_CACHE[cache_key] = candidate

            return candidate

    # --------------------------------------------------
    # caller directory
    # --------------------------------------------------

    if start is None:

        caller = Path(
            inspect.currentframe().f_back.f_code.co_filename
        ).resolve()

        start = caller.parent

    else:

        start = Path(start).resolve()

    # --------------------------------------------------
    # current + parents
    # --------------------------------------------------

    current = start

    while True:

        candidate = current / filename

        if candidate.is_file():

            candidate = candidate.resolve()

            _FILE_CACHE[cache_key] = candidate

            return candidate

        if current.parent == current:
            break

        current = current.parent

    # --------------------------------------------------
    # search downward
    # --------------------------------------------------

    current = start

    while True:

        found = _search_down(
            current,
            filename.name,
        )

        if found:

            _FILE_CACHE[cache_key] = found

            return found

        if current.parent == current:
            break

        current = current.parent

    raise FileNotFoundError(
        f"Cannot locate '{filename}'."
    )