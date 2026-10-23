# resolve_path/add_root.py
from __future__ import annotations # -> phải đặt đầu file

import inspect,sys
from pathlib import Path
from typing import Optional,Iterable

__all__ = ["add_project_root","add_project_root_pkgs"]

_PROJECT_ROOT: Path | None = None

# Cache project root
_PROJECT_ROOT: Optional[Path] = None


def _is_package(path: Path, package_name: str) -> bool:
    """Kiểm tra path có chứa package_name hay không."""
    pkg = path / package_name
    return pkg.is_dir() and (pkg / "__init__.py").exists()


def _search_down(start: Path, package_name: str) -> Optional[Path]:
    """Tìm project root bằng cách duyệt xuống."""
    try:
        for pkg in start.rglob(package_name):
            if pkg.is_dir() and (pkg / "__init__.py").exists():
                return pkg.parent.resolve()
    except PermissionError:
        pass

    return None


def add_project_root(package_name: str = "dsl_scan") -> Path:
    """
    Tự động thêm project root vào sys.path.

    Thuật toán:

    1. Lấy file đang gọi hàm.
    2. Nếu thư mục hiện tại chứa package -> dùng luôn.
    3. Dò ngược lên các thư mục cha.
    4. Nếu vẫn không thấy thì dò xuống.
    5. Cache kết quả.

    Ví dụ:

        PyJP3_313/
        │
        ├── dsl_scan/
        │     ├── __init__.py
        │     └── ...
        │
        ├── tests/
        └── scripts/

    Có thể gọi từ bất kỳ đâu:

        add_project_root("dsl_scan")
    """

    global _PROJECT_ROOT

    if _PROJECT_ROOT is not None:
        return _PROJECT_ROOT

    # File gọi add_project_root()
    caller = Path(inspect.stack()[1].filename).resolve()

    start = caller.parent

    # --------------------------------------------------
    # Trường hợp 1:
    # caller đang ở project root
    # --------------------------------------------------

    if _is_package(start, package_name):
        root = start

    else:

        # --------------------------------------------------
        # Trường hợp 2:
        # dò ngược lên
        # --------------------------------------------------

        root = None

        current = start

        while True:

            if _is_package(current, package_name):
                root = current
                break

            if current.parent == current:
                break

            current = current.parent

        # --------------------------------------------------
        # Trường hợp 3:
        # dò xuống
        # --------------------------------------------------

        if root is None:
            root = _search_down(start, package_name)

    if root is None:
        raise RuntimeError(
            f"Cannot locate project root containing package '{package_name}'."
        )

    root = root.resolve()

    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    _PROJECT_ROOT = root

    return root

# ----------------------------------------------------------------------
# Utilities
# ----------------------------------------------------------------------

def _normalize_packages(*packages) -> tuple[str, ...]:
    """
    Chuẩn hóa package.

    Hỗ trợ:

        add_project_root("dsl_scan")

        add_project_root("dsl_scan", "modules")

        add_project_root(["dsl_scan", "modules"])

        add_project_root(("dsl_scan", "modules"))

        add_project_root({"dsl_scan", "modules"})
    """

    # Nếu truyền đúng 1 iterable (list/tuple/set)
    if (
        len(packages) == 1
        and isinstance(packages[0], Iterable)
        and not isinstance(packages[0], (str, bytes))
    ):
        packages = tuple(packages[0])

    packages = tuple(str(x) for x in packages)

    # bỏ trùng nhưng giữ thứ tự
    packages = tuple(dict.fromkeys(packages))

    if not packages:
        raise ValueError("At least one package is required.")

    return packages


def _contains_packages(
    root: Path,
    packages: tuple[str, ...],
) -> bool:
    
    """
    Return True nếu root chứa đầy đủ các package yêu cầu.
    """
    return all(
        (root / pkg).is_dir()
        and (root/pkg/"__init__.py").is_file()
        for pkg in packages
    )

    # """
    # Check whether root contains all required packages.
    # """
    # for pkg in packages:

    #     pkg_dir = root / pkg

    #     if not (
    #         pkg_dir.is_dir()
    #         and (pkg_dir / "__init__.py").exists()
    #     ):
    #         return False

    # return True


def _search_down_pkgs(
    start: Path,
    packages: tuple[str, ...],
) -> Path | None:
    """
    Search recursively for a directory
    containing all required packages.
    """

    stack = [start]

    while stack:

        current = stack.pop()

        if _contains_packages(current, packages):
            return current.resolve()

        try:

            for child in current.iterdir():

                if child.is_dir():

                    # bỏ qua thư mục cache
                    if child.name in {
                        "__pycache__",
                        ".git",
                        ".svn",
                        ".hg",
                        ".idea",
                        ".vscode",
                        "node_modules",
                        ".venv",
                        "venv",
                        "dist",
                        "build",
                    }:
                        continue

                    stack.append(child)

        except PermissionError:
            pass

    return None

# def _search_down_pkgs(
#     start: Path,
#     packages: tuple[str, ...],
# ) -> Path | None:
#     """
#     Search downward for the first directory
#     containing all required packages.
#     """

#     try:

#         for path in start.rglob("*"):

#             if not path.is_dir():
#                 continue

#             if _contains_packages(path, packages):
#                 return path.resolve()

#     except PermissionError:
#         pass

#     return None


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------

def add_project_root_pkgs(
    *packages: str | Iterable[str],
) -> Path:
    """
    Locate the project root and add it to sys.path.

    Search order
    ------------

    1. Current caller directory.

    2. Parent directories.

    3. Recursive downward search.

    Parameters
    ----------
    packages:
        Package name or iterable of package names.

        Examples::

            add_project_root("dsl_scan")

            add_project_root(
                (
                    "dsl_scan",
                    "jp_modules",
                    "modules",
                )
            )

    Returns
    -------
    pathlib.Path
        Project root.

    Raises
    ------
    RuntimeError
        Project root cannot be found.
    """

    global _PROJECT_ROOT

    if _PROJECT_ROOT is not None:
        return _PROJECT_ROOT

    packages = _normalize_packages(*packages)

    # --------------------------------------------------

    caller = Path(
        inspect.stack()[1].filename
    ).resolve()

    start = caller.parent

    # --------------------------------------------------
    # Case 1 : current directory
    # --------------------------------------------------

    if _contains_packages(start, packages):

        root = start

    else:

        root = None

        # --------------------------------------------------
        # Case 2 : search upward
        # --------------------------------------------------

        current = start

        while True:

            if _contains_packages(
                current,
                packages,
            ):
                root = current
                break

            if current.parent == current:
                break

            current = current.parent

        # --------------------------------------------------
        # Case 3 : search downward
        # --------------------------------------------------

        if root is None:
            root = _search_down_pkgs(
                start,
                packages,
            )

    # --------------------------------------------------

    if root is None:

        raise RuntimeError(
            "Cannot locate project root.\n"
            f"Required packages: {packages}"
        )

    root = root.resolve()

    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    _PROJECT_ROOT = root

    return root