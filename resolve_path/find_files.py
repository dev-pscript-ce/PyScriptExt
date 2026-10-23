from __future__ import annotations

from pathlib import Path

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


def find_file(
    filename: str,
    *,
    start: str | Path | None = None,
) -> Path:
    """
    Tìm file theo thứ tự:

        1. start
        2. các thư mục cha
        3. dò xuống từ từng thư mục cha

    Parameters
    ----------
    filename:
        Ví dụ "main.ps"

    start:
        Thư mục bắt đầu.
        Mặc định = thư mục chứa file đang chạy.

    Returns
    -------
    Path

    Raises
    ------
    FileNotFoundError
    """

    if start is None:
        start = Path.cwd()
    else:
        start = Path(start).resolve()

    # --------------------------------------------------
    # current + parents
    # --------------------------------------------------

    current = start

    while True:

        candidate = current / filename

        if candidate.is_file():
            return candidate.resolve()

        if current.parent == current:
            break

        current = current.parent

    # --------------------------------------------------
    # search downward
    # --------------------------------------------------

    current = start

    while True:

        stack = [current]

        while stack:

            folder = stack.pop()

            candidate = folder / filename

            if candidate.is_file():
                return candidate.resolve()

            try:

                children = sorted(
                    (
                        x
                        for x in folder.iterdir()
                        if x.is_dir()
                        and x.name not in _SKIP_DIRS
                    ),
                    reverse=True,
                )

                stack.extend(children)

            except (PermissionError, OSError):
                pass

        if current.parent == current:
            break

        current = current.parent

    raise FileNotFoundError(filename)