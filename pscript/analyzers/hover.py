from __future__ import annotations

import json
import sys,re

from pscript.parsers import Parser
from pscript.scanners.scanner import Scanner

from .analyzer import AnalyzerSource

from.core.definitions import (
    MODULES,
    BUILTINS,
)
from .core.resolve import resolve_path

class HoverAnalyzer:

    def __init__(
        self,
        tree,
    ):
        self.tree = tree

        self.analyzer = AnalyzerSource([])

        self.analyzer.diagnostic(
            tree
        )

    # =========================================
    # Resolve
    # =========================================

    def resolve(
        self,
        path,
    ):
        

        if not isinstance(
            path,
            str,
        ):
            return None

        path = path.strip()

        if not path:
            return None

        # =========================================
        # Built-in object / namespace
        # =========================================

        if "." not in path:

            builtin_objects = (
                BUILTINS.get(
                    "objects",
                    {},
                )
            )

            method = builtin_objects.get(
                path
            )

            if method is not None:

                return self.create_result(
                    name=path,
                    method=method,
                    type="Built-in",
                )

        # =========================================
        # Module root
        # =========================================

        if "." not in path:

            resolved_name = (
                self.analyzer.module_aliases.get(
                    path,
                    path,
                )
            )

            if resolved_name in MODULES:

                module = MODULES.get(
                    resolved_name
                )

                if module is not None:

                    return self.create_result(
                        name=path,
                        method=module,
                        type=f"Module: {resolved_name}",
                    )

        # =========================================
        # Built-in / Module
        # =========================================

        method = resolve_path(
            path=path,
            imported_modules=(
                self.analyzer.imported_modules
            ),
        )

        if method is not None:

            # -------------------------------------
            # Module
            # -------------------------------------

            if "." in path:

                root = path.split(
                    ".",
                    1,
                )[0]

                resolved_name = (
                    self.analyzer.module_aliases.get(
                        root,
                        root,
                    )
                )

                if resolved_name in MODULES:

                    return self.create_result(
                        name=path,
                        method=method,
                        type=(
                            f"Module: "
                            f"{resolved_name}"
                        ),
                    )

                # ---------------------------------
                # Built-in object
                # ---------------------------------

                return self.create_result(
                    name=path,
                    method=method,
                    type="Built-in",
                )

            # -------------------------------------
            # Global builtin
            # -------------------------------------

            builtin_methods = (
                BUILTINS.get(
                    "methods",
                    {},
                )
            )

            if path in builtin_methods:

                return self.create_result(
                    name=path,
                    method=method,
                    type="Built-in",
                )

        # =========================================
        # Imported function / symbol
        # =========================================

        if "." not in path:

            symbol = (
                self.analyzer.scopes.resolve(
                    path
                )
            )

            if symbol is not None:

                if symbol.kind == "import":

                    imported_method = getattr(
                        symbol,
                        "data",
                        None,
                    )

                    if imported_method is not None:

                        return self.create_result(
                            name=path,
                            method=imported_method,
                            type="Imported function",
                        )

        # =========================================
        # User-defined
        # =========================================

        if "." not in path:

            result = self.user_defined(
                path,
            )

            if result is not None:
                return result

        return None

    
    def user_defined(
        self,
        name,
    ):
        symbol = self.analyzer.scopes.resolve(
            name,
        )

        if symbol is None:
            return None

        # =========================================
        # User-defined function
        # =========================================

        if symbol.kind == "user_defined_function":

            node = getattr(
                symbol,
                "node",
                None,
            )

            if node is None:
                return None

            method = {
                "parameters": node.params,
            }

            return self.create_result(
                name=name,
                method=method,
                type="User defined function",
            )

        # =========================================
        # User-defined class
        # =========================================

        if symbol.kind == "user_defined_class":

            node = getattr(
                symbol,
                "node",
                None,
            )

            if node is None:
                return None

            method = {
                "parameters": [],
                "methods": [],
            }

            return self.create_result(
                name=name,
                method=method,
                type="User-defined class",
            )

        return None

    # =========================================
    # Built-in
    # =========================================

    def builtin(
        self,
        name,
    ):

        return self.resolve(
            name,
        )

    # =========================================
    # Built-in member
    # =========================================

    def builtin_member(
        self,
        object_name,
        member_name,
    ):

        path = (
            f"{object_name}."
            f"{member_name}"
        )

        return self.resolve(
            path,
        )

    # =========================================
    # Built-in path
    # =========================================

    def builtin_path(
        self,
        path,
    ):

        return self.resolve(
            path,
        )

    # =========================================
    # Module
    # =========================================

    def module_method(
        self,
        module_name,
        method_name,
    ):

        path = (
            f"{module_name}."
            f"{method_name}"
        )

        return self.resolve(
            path,
        )

    # =========================================
    # Imported function
    # =========================================

    def imported_function(
        self,
        name,
    ):

        return self.resolve(
            name,
        )

    # =========================================
    # Result
    # =========================================

    @staticmethod

    def create_result(
        name,
        method,
        type,
    ):

        if not isinstance(
            method,
            dict,
        ):
            return None

        parameters = method.get(
            "parameters",
            [],
        )

        args = []

        result_parameters = []

        for parameter in parameters:

            # =====================================
            # AST Parameter
            # =====================================

            parameter_name = getattr(
                parameter,
                "name",
                None,
            )

            if parameter_name:

                args.append(
                    parameter_name
                )

                result_parameters.append({
                    "name": parameter_name,
                    "required": (
                        parameter.default is None
                    ),
                })

                continue

            # =====================================
            # Metadata dict
            # =====================================

            if isinstance(
                parameter,
                dict,
            ):

                parameter_name = parameter.get(
                    "name",
                    "",
                )

                if parameter_name:

                    args.append(
                        parameter_name
                    )

                    result_parameters.append(
                        parameter
                    )

        # =========================================
        # Object / namespace
        # =========================================

        if (
            "methods" in method
            and not parameters
        ):

            signature = name

        else:

            signature = (
                f"{name}"
                f"({', '.join(args)})"
            )

        return {
            "name": name,

            "signature": signature,

            "description": method.get(
                "description",
                "",
            ),

            "type": type,

            "parameters": result_parameters,
        }

# =============================================
# Main hover logic
# =============================================

def find_token_at_position(
    tokens,
    line,
    column,
):

    for token in tokens:

        token_line = token.line - 1
        token_column = token.column - 1

        token_end = (
            token_column
            + token.length
        )

        if (
            token_line == line
            and token_column
            <= column
            < token_end
        ):
            return token

    return None

def hover(
    source,
    line,
    column,
):

    scanner = Scanner(source)

    tokens = scanner.scan()

    parser = Parser(tokens)

    tree = parser.parse()

    analyzer = HoverAnalyzer(tree)

    # -----------------------------------------
    # Token tại vị trí cursor
    # -----------------------------------------

    token = find_token_at_position(
        tokens,
        line,
        column,
    )

    if token is None:
        return None

    # -----------------------------------------
    # Chỉ IDENT mới được resolve
    # -----------------------------------------

    if token.kind != "IDENT":
        return None

    word = token.value

    # -----------------------------------------
    # Dòng hiện tại
    # -----------------------------------------

    lines = source.splitlines()

    if line < 0 or line >= len(lines):
        return None

    line_text = lines[line]

    # Token column của Pscript là 1-based
    start = token.column - 1

    end = (
        start
        + token.length
    )

    # =========================================
    # module.method
    # =========================================

    before = line_text[:start].rstrip()

    match = re.search(
        r"([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\.$",
        before,
    )

    if match:

        parent_path = match.group(1)

        builtin_path = (
            f"{parent_path}.{word}"
        )

        result = analyzer.builtin_path(
            builtin_path,
        )

        if result is not None:
            return result

        # Sau đó mới thử module method

    # =========================================
    # Imported function
    # =========================================

    result = analyzer.imported_function(
        word,
    )

    if result is not None:
        return result

    # =========================================
    # User-defined function / class
    # =========================================

    result = analyzer.user_defined(
        word,
    )

    if result is not None:
        return result

    # =========================================
    # Built-in
    # =========================================

    return analyzer.builtin(
        word,
    )



# =============================================
# CLI
# =============================================

def main():

    # -----------------------------------------
    # Arguments:
    # argv[0] = module
    # argv[1] = line
    # argv[2] = column
    # -----------------------------------------

    if len(sys.argv) < 3:

        print(
            json.dumps(None)
        )

        return

    try:

        line = int(
            sys.argv[1]
        )

        column = int(
            sys.argv[2]
        )

        # -------------------------------------
        # Nhận source từ VS Code buffer
        # -------------------------------------

        source = sys.stdin.read()

        # -------------------------------------
        # Phân tích Signature
        # -------------------------------------

        result = hover(
            source=source,
            line=line,
            column=column,
        )

        # -------------------------------------
        # Trả JSON cho VS Code
        # -------------------------------------

        print(
            json.dumps(
                result,
                ensure_ascii=False,
            )
        )

    except Exception as error:

        print(
            json.dumps(
                {
                    "error": str(error),
                },
                ensure_ascii=False,
            )
        )

if __name__ == "__main__":
    main()