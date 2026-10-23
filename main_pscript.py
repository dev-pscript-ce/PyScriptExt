import sys
sys.dont_write_bytecode = True
import argparse
from pathlib import Path

if getattr(sys, "frozen", False):
    ROOT = Path(sys._MEIPASS)
else:
    from resolve_path.add_pkg import add_root_project_pkg
    ROOT = add_root_project_pkg("pscript")

from pscript.scanners.scanner import Scanner
from pscript.parsers import Parser
from pscript.interpreters.interpreter import Interpreter
from pscript.runtimes.runtime import Runtime

from pscript.debugs.ast_printer import ASTPrinter
from pscript.debugs.token_printer import TokenPrinter
from pscript.debugs.debug import debug

def run(
    file,
    workspace_root=None,
    show_ast=False,
    show_token=False,
    debug_groups=(),
):
    # =========================================
    # File
    # =========================================

    file = Path(file).resolve()

    if not file.exists():
        raise FileNotFoundError(
            f"File not found: {file}"
        )

    if file.suffix.lower() != ".ps":
        raise ValueError(
            f"Unsuported file type: {file.suffix or '<none'}"
        )

    # =========================================
    # Workspace
    # =========================================

    if workspace_root is None:
        workspace_root = file.parent
    else:
        workspace_root = Path(
            workspace_root
        ).resolve()

        if not workspace_root.exists():
            raise NotADirectoryError(f"Workspace not found: {workspace_root}")
        if not workspace_root.is_dir():
            raise NotADirectoryError(
                f"Workspace is not a directory: {workspace_root}"
            )

    # =========================================
    # Debug
    # =========================================

    debug.flags.clear()
    debug.enable_group(*debug_groups)

    # =========================================
    # Runtime
    # =========================================

    runtime = Runtime(
        project_root=workspace_root
    )

    runtime.file_stack.append(file)

    # =========================================
    # Scanner
    # =========================================

    source = file.read_text(
        encoding="utf8"
    )

    scanner = Scanner(source)

    tokens = scanner.scan()

    if show_token:
        TokenPrinter().print(tokens)

    # =========================================
    # Parser
    # =========================================

    parser = Parser(tokens)

    tree = parser.parse()

    if show_ast:
        ASTPrinter().print(tree)

    # =========================================
    # Interpreter
    # =========================================

    interpreter = Interpreter(
        runtime=runtime
    )

    interpreter.visit(tree)

def main():

    parser = argparse.ArgumentParser(
        prog="pscript",
        description="Pscript programming language"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Pscript 0.1.0"
    )

    parser.add_argument(
        "file",
        help="Pscript source file (.ps)"
    )

    parser.add_argument(
        "workspace",
        nargs="?",
        help="Pscript workspace root"
    )

    parser.add_argument(
        "--ast",
        action="store_true",
        help="Print AST"
    )

    parser.add_argument(
        "--tokens",
        action="store_true",
        help="Print tokens"
    )

    parser.add_argument(
        "--debug",
        nargs="*",
        default=[],
        help="Enable debug groups"
    )

    args = parser.parse_args()

    # =========================================
    # File
    # =========================================

    file = args.file
    
    # =========================================
    # Workspace
    # =========================================

    if args.workspace:
        workspace_root = Path(
            args.workspace
        ).resolve()
    else:
        workspace_root = Path(
            file
        ).resolve().parent

    # =========================================
    # Run
    # =========================================

    try:
        run(
            file=file,
            workspace_root=workspace_root,
            show_ast=args.ast,
            show_token=args.tokens,
            debug_groups=args.debug,
        )

    except FileNotFoundError as e:
        print(
            f"Pscript: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    except ValueError as e:
        print(
            f"Pscript: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    except NotADirectoryError as e:
        print(
            f"Pscript: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()




