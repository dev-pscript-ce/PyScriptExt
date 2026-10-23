from __future__ import annotations

import json
import sys

from pscript.parsers import Parser
from pscript.scanners.scanner import Scanner

from .analyzer import AnalyzerSource
from .core.resolve import resolve_path

class SignatureAnalyzer:

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
    # Resolve path
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
        # Built-in / Module
        # =========================================

        method = resolve_path(
            path=path,
            imported_modules=(
                self.analyzer.imported_modules
            ),
        )

        if method is not None:

            return {
                "name": path,

                "parameters": method.get(
                    "parameters",
                    [],
                ),

                "description": method.get(
                    "description",
                    "",
                ),
            }

        # =========================================
        # Imported function
        #
        # from ocr import find_text
        # find_text()
        # =========================================

        if "." not in path:

            symbol = (
                self.analyzer.scopes.resolve(
                    path
                )
            )

            if symbol is None:
                return None

            if symbol.kind != "import":
                return None

            method = getattr(
                symbol,
                "data",
                None,
            )

            if method is None:
                return None

            return {
                "name": path,

                "parameters": method.get(
                    "parameters",
                    [],
                ),

                "description": method.get(
                    "description",
                    "",
                ),
            }

        return None

    # =========================================
    # Module method
    # =========================================

    def find_module_method(
        self,
        module_name,
        method_name,
    ):

        return self.resolve(
            f"{module_name}.{method_name}"
        )

    # =========================================
    # Built-in
    # =========================================

    def find_builtin(
        self,
        function_name,
    ):

        return self.resolve(
            function_name,
        )

    # =========================================
    # Built-in object method
    # =========================================

    def find_builtin_member(
        self,
        path,
    ):

        if "." not in path:
            return None

        return self.resolve(
            path,
        )

    # =========================================
    # Imported function
    # =========================================

    def find_imported_function(
        self,
        function_name,
    ):

        return self.resolve(
            function_name,
        )

    def find_user_function(self, name):
        symbol = self.analyzer.scopes.resolve(name)

        if symbol is None:
            return None

        if symbol.kind != "user_defined_function":
            return None

        node = getattr(symbol, "node", None)

        if node is None:
            return None

        parameters = []

        for parameter in node.params:
            parameters.append({
                "name": parameter.name,
                "required": parameter.default is None,
            })

        return {
            "name": name,
            "parameters": parameters,
            "description": "",
        }



# =============================================
# Helpers
# =============================================

def parameter_name(
    parameter,
):

    if not isinstance(
        parameter,
        dict,
    ):
        return str(parameter)

    return parameter.get(
        "name",
        "",
    )


def parameter_description(
    parameter,
):

    if not isinstance(
        parameter,
        dict,
    ):
        return ""

    return parameter.get(
        "description",
        "",
    )


# =============================================
# Signature
# =============================================

def signature(
    source,
    line,
    column,
):

    scanner = Scanner(source)

    tokens = scanner.scan()

    parser = Parser(tokens)

    tree = parser.parse()

    analyzer = SignatureAnalyzer(
        tree
    )

    lines = source.splitlines()

    if line < 0 or line >= len(lines):
        return None

    line_text = lines[line]

    if column < 0:
        column = 0

    if column > len(line_text):
        column = len(line_text)

    before_cursor = line_text[
        :column
    ]

    # =========================================
    # module.method(
    # =========================================

    module_match = None

    import re

    module_match = re.search(
        r"([A-Za-z_]\w*(?:\.[A-Za-z_]\w+)*)" 
        r"\((.*)$", 
        before_cursor, 
    )

    if module_match:

        function_path = (
            module_match.group(1)
        )


        arguments_text = (
            module_match.group(2)
        )

        method = analyzer.find_builtin_member(
            function_path,
        )

        if method is not None:

            return create_signature(
                method,
                arguments_text,
            )

    # =========================================
    # function(
    # =========================================

    builtin_match = re.search(
        r"([A-Za-z_]\w*)"
        r"\((.*)$",
        before_cursor,
    )

    if builtin_match:

        function_name = (
            builtin_match.group(1)
        )

        arguments_text = (
            builtin_match.group(2)
        )

        # -----------------------------
        # Imported function
        # -----------------------------

        method = (
            analyzer.find_imported_function(
                function_name,
            )
        )

        if method is None:

            # -------------------------
            # Built-in
            # -------------------------

            method = analyzer.find_builtin(
                function_name,
            )

        if method is None:
            method = analyzer.find_user_function(
                function_name
            )

        if method is not None:

            return create_signature(
                method,
                arguments_text,
            )

    return None


# =============================================
# Create result
# =============================================

def active_parameter_index(
    arguments_text,
):

    depth = 0
    index = 0

    for char in arguments_text:

        if char == "(":
            depth += 1

        elif char == ")":
            depth -= 1

        elif char == "," and depth == 0:
            index += 1

    return index

def create_signature(
    method,
    arguments_text,
):

    parameters = method.get(
        "parameters",
        [],
    )

    parameter_data = []

    for parameter in parameters:

        parameter_data.append(
            {
                "name": parameter_name(
                    parameter
                ),
                "description": parameter_description(
                    parameter
                ),
            }
        )

    names = [
        item["name"]
        for item in parameter_data
        if item["name"]
    ]

    args = ", ".join(names)

    active_parameter = 0

    if arguments_text.strip():

        active_parameter = (
            active_parameter_index(
                arguments_text
            )
        )

    if parameter_data:

        active_parameter = min(
            active_parameter,
            len(parameter_data) - 1,
        )

    else:

        active_parameter = 0

    return {
        "name": method["name"],
        "signature": (
            f'{method["name"]}'
            f'({args})'
        ),
        "description": method.get(
            "description",
            "",
        ),
        "parameters": parameter_data,
        "activeParameter": active_parameter,
    }


# =============================================
# CLI
# =============================================


def main():

    # -----------------------------------------
    # Arguments:
    #
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

        result = signature(
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