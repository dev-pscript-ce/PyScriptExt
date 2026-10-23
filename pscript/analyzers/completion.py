from __future__ import annotations
import sys
sys.dont_write_bytecode=True

import json
import re

from pscript.parsers import Parser
from pscript.scanners.scanner import Scanner

from .analyzer import AnalyzerSource

from pscript.asts.expressions import (
    MemberAccess,
    Variable
)
from .core.definitions import(
    KEYWORDS,
    CONSTANTS,
    MODULES,
    BUILTINS,
)
from .core.resolve import resolve_namespace
# ============================================
# Completion Analyzer
# ============================================

class CompletionAnalyzer:

    def __init__(
        self,
        tree,
        imported_modules=None,
    ):

        self.tree = tree

        self.analyzer = AnalyzerSource(
            [],
        )

        if tree is not None:

            self.analyzer.diagnostic(
                tree,
            )

        if imported_modules:

            self.analyzer.imported_modules.update(
                imported_modules
            )


    # =========================================
    # Namespace
    # =========================================

    def resolve(
        self,
        path,
    ):
        
        return resolve_namespace(
            path=path,

            imported_modules=(
                self.analyzer.imported_modules
            ),

            module_aliases=(
                self.analyzer.module_aliases
            ),
        )

    # =========================================
    # Member
    # =========================================

    def find_member(
        self,
        object_name,
    ):

        namespace = self.resolve(
            object_name,
        )

        if namespace is None:
            return []

        methods = namespace.get(
            "methods",
            {},
        )

        result = []

        for name, method in methods.items():

            parameters = method.get(
                "parameters",
                [],
            )

            result.append(
                {
                    "label": name,

                    "kind": "method",

                    "detail": (
                        f"{name}"
                        f"("
                        f"{self.parameter_text(parameters)}"
                        f")"
                    ),

                    "parameters": parameters,

                    "documentation": (
                        method.get(
                            "description",
                            "",
                        )
                    ),

                    "insertText": (
                        f"{name}"
                        f"("
                        f"{self.snippet_parameters(parameters)}"
                        f"$0)"
                    ),

                    "insertTextFormat": 2,
                }
            )

        return result

    # =========================================
    # Function call
    # =========================================

    def find_call(
        self,
        function_name,
    ):

        # -------------------------------------
        # Member call
        #
        # ocr.FIND_TEXT(
        # cv2.FIND_IMG(
        # -------------------------------------

        if "." in function_name:

            parts = function_name.split(".")

            object_name = ".".join(
                parts[:-1]
            )

            method_name = parts[-1]

            namespace = self.resolve(
                object_name,
            )

            if namespace is None:
                return []

            methods = namespace.get(
                "methods",
                {},
            )

            method = methods.get(
                method_name,
            )

            if method is None:
                return []

            return [
                self.method_completion(
                    method_name,
                    method,
                )
            ]

        # -------------------------------------
        # User-defined / imported function
        # -------------------------------------

        scope = (
            self.analyzer.scopes.global_scope
        )

        symbol = scope.symbols.get(
            function_name,
        )

        if symbol is not None:

            return [
                self.symbol_completion(
                    function_name,
                    symbol,
                )
            ]

        # -------------------------------------
        # Builtin
        # -------------------------------------

        methods = BUILTINS.get(
            "methods",
            {},
        )

        method = methods.get(
            function_name,
        )

        if method is not None:

            return [
                self.function_completion(
                    function_name,
                    method,
                )
            ]

        obj = BUILTINS.get("objects", {}).get(function_name)

        if obj is not None and obj.get("callable",False):
            return [
                self.object_completion(function_name, obj)
            ]

        return []

    def method_completion(
        self,
        name,
        method,
    ):

        parameters = method.get(
            "parameters",
            [],
        )

        return {
            "label": name,

            "kind": "method",

            "detail": (
                f"{name}"
                f"("
                f"{self.parameter_text(parameters)}"
                f")"
            ),

            "parameters": parameters,

            "documentation": (
                method.get(
                    "description",
                    "",
                )
            ),

            "insertText": (
                f"{name}"
                f"("
                f"{self.snippet_parameters(parameters)}"
                f"$0)"
            ),

            "insertTextFormat": 2,
        }

    
    def object_completion(self, name, obj):
        parameters = obj.get("parameters", [])
        callable_object = obj.get("callable", False)

        return {
            "label": name,
            "kind": "function" if callable_object else "variable",
            "detail": (
                f"{name}({self.parameter_text(parameters)})"
                if callable_object
                else f"object {name}"
            ),
            "parameters": parameters,
            "documentation": obj.get("description", ""),
            "insertText": (
                f"{name}("
                f"{self.snippet_parameters(parameters)}"
                f"$0)"
                if callable_object
                else name
            ),
            "insertTextFormat": 2 if callable_object else 1,
        }

    # =========================================
    # Global symbols
    # =========================================
    def global_symbols(self):

        result = []

        scope = (
            self.analyzer.scopes.global_scope
        )

        for name, symbol in (
            scope.symbols.items()
        ):

            result.append(
                self.symbol_completion(
                    name,
                    symbol,
                )
            )

        return result

    def function_completion(
        self,
        name,
        method,
    ):

        parameters = method.get(
            "parameters",
            [],
        )

        return {
            "label": name,

            "kind": "function",

            "detail": (
                f"{name}"
                f"("
                f"{self.parameter_text(parameters)}"
                f")"
            ),

            "parameters": parameters,

            "documentation": (
                method.get(
                    "description",
                    "",
                )
            ),

            "insertText": (
                f"{name}"
                f"("
                f"{self.snippet_parameters(parameters)}"
                f"$0)"
            ),

            "insertTextFormat": 2,
        }

    # =========================================
    # Import completion
    # =========================================

    def import_completion(
        self,
        name,
        method,
    ):

        parameters = method.get(
            "parameters",
            [],
        )

        return {
            "label": name,

            "kind": "function",

            "detail": (
                f"{name}"
                f"("
                f"{self.parameter_text(parameters)}"
                f")"
            ),

            "parameters": parameters,

            "documentation": (
                method.get(
                    "description",
                    "",
                )
            ),

            "insertText": name,

            "insertTextFormat": 1,
        }


    def find_imports(
        self,
        module_name,
    ):

        namespace = self.resolve(
            module_name,
        )

        if namespace is None:
            return []

        methods = namespace.get(
            "methods",
            {},
        )

        result = []

        for name, method in methods.items():

            result.append(
                self.import_completion(
                    name,
                    method,
                )
            )

        return result
    
    def find_modules(self):

        result = []

        for name in MODULES:

            result.append(
                {
                    "label": name,
                    "kind": "module",
                    "detail": f"module {name}",
                    "insertText": name,
                    "insertTextFormat": 1,
                }
            )

        return result

    # =========================================
    # Builtins
    # =========================================

    def builtin_symbols(self):

        result = []

        methods = BUILTINS.get(
            "methods",
            {},
        )

        for name, method in methods.items():

            parameters = method.get(
                "parameters",
                [],
            )

            result.append(
                {
                    "label": name,

                    "kind": "function",

                    "detail": (
                        f"{name}"
                        f"("
                        f"{self.parameter_text(parameters)}"
                        f")"
                    ),

                    "parameters": parameters,

                    "documentation": (
                        method.get(
                            "description",
                            "",
                        )
                    ),

                    "insertText": (
                        f"{name}"
                        f"("
                        f"{self.snippet_parameters(parameters)}"
                        f"$0)"
                    ),

                    "insertTextFormat": 2,
                }
            )
        obj = BUILTINS.get("objects",{})

        for name,obj in obj.items():
            result.append(self.object_completion(name, obj))

        return result

    # =========================================
    # Keywords
    # =========================================

    def keyword_symbols(self):

        return [
            {
                "label": keyword,
                "kind": "keyword",
                "detail": "Pscript keyword",
            }

            for keyword in KEYWORDS
        ]

    # =========================================
    # Constants
    # =========================================

    def constant_symbols(self):

        return [
            {
                "label": constant,
                "kind": "constant",
                "detail": "Pscript constant",
            }

            for constant in CONSTANTS
        ]

    # =========================================
    # Parameter text
    # =========================================

    @staticmethod
    def parameter_text(
        parameters,
    ):

        result = []

        for parameter in parameters:

            if not isinstance(
                parameter,
                dict,
            ):
                continue

            name = parameter.get(
                "name",
                "",
            )

            if not name:
                continue

            if parameter.get(
                "required",
                True,
            ):

                result.append(
                    name
                )

            else:

                result.append(
                    f"[{name}]"
                )

        return ", ".join(
            result
        )

    # =========================================
    # Snippet
    # =========================================

    @staticmethod
    def snippet_parameters(
        parameters,
    ):

        if not parameters:
            return ""

        values = []

        index = 1

        for parameter in parameters:

            if not isinstance(
                parameter,
                dict,
            ):
                continue

            name = parameter.get(
                "name",
                "",
            )

            if not name:
                continue

            # Không phải variadic
            if parameter.get(
                "variadic",
                False,
            ):
                continue

            # *args / **kwargs
            if name.startswith("*"):
                continue

            # Chỉ required
            if not parameter.get(
                "required",
                True,
            ):
                continue

            values.append(
                f"${{{index}:{name}}}"
            )

            index += 1

        return ", ".join(
            values
        )

    # =========================================
    # Symbol kind
    # =========================================

    @staticmethod
    def symbol_kind(
        kind,
    ):

        mapping = {
            "variable": "variable",
            "func": "function",
            "params": "variable",
            "import": "function",
            "module": "module",
        }

        return mapping.get(
            kind,
            "text",
        )

    # =========================================
    # Symbol completion
    # =========================================

    def symbol_completion(
        self,
        name,
        symbol,
    ):

        if symbol.kind == "import":

            method = getattr(
                symbol,
                "data",
                None,
            )

            if isinstance(
                method,
                dict,
            ):

                parameters = method.get(
                    "parameters",
                    [],
                )

                return {
                    "label": name,

                    "kind": "function",

                    "detail": (
                        f"{name}"
                        f"("
                        f"{self.parameter_text(parameters)}"
                        f")"
                    ),

                    "parameters": parameters,

                    "documentation": (
                        method.get(
                            "description",
                            "",
                        )
                    ),

                    "insertText": (
                        f"{name}"
                        f"("
                        f"{self.snippet_parameters(parameters)}"
                        f"$0)"
                    ),

                    "insertTextFormat": 2,
                }

        # =========================================
        # User-defined function
        # =========================================

        if symbol.kind == "user_defined_function":

            node = getattr(
                symbol,
                "node",
                None,
            )

            if node is not None:

                parameters = []

                for parameter in node.params:

                    parameters.append(
                        {
                            "name": parameter.name,

                            "required": (
                                parameter.default is None
                            ),
                        }
                    )

                return {
                    "label": name,

                    "kind": "function",

                    "detail": (
                        f"{name}"
                        f"("
                        f"{self.parameter_text(parameters)}"
                        f")"
                    ),

                    "parameters": parameters,

                    "documentation": "",

                    "insertText": (
                        f"{name}"
                        f"("
                        f"{self.snippet_parameters(parameters)}"
                        f"$0)"
                    ),

                    "insertTextFormat": 2,
                }

        # =========================================
        # User-defined class
        # =========================================

        if symbol.kind == "user_defined_class":

            node = getattr(
                symbol,
                "node",
                None,
            )

            if node is not None:

                return {
                    "label": name,

                    "kind": "class",

                    "detail": (
                        f"class "
                        f"{name}"
                    ),

                    "documentation": "",

                    "insertText": name,

                    "insertTextFormat": 1,
                }

        # =========================================
        # Logic cũ - giữ nguyên
        # =========================================

        return {
            "label": name,

            "kind": self.symbol_kind(
                symbol.kind,
            ),

            "detail": (
                f"{symbol.kind} "
                f"{name}"
            ),
        }
    # =========================================
    # Object name
    # =========================================

    def get_object_name(
        self,
        node,
    ):

        if isinstance(
            node,
            Variable,
        ):
            return node.name

        if isinstance(
            node,
            MemberAccess,
        ):

            left = self.get_object_name(
                node.obj
            )

            if left is None:
                return None

            return (
                f"{left}."
                f"{node.member}"
            )

        return None


# ============================================
# Filter prefix
# ============================================

def filter_items(
    items,
    prefix,
):

    if not prefix:
        return items

    prefix_lower = prefix.lower()

    return [
        item
        for item in items

        if item.get(
            "label",
            "",
        ).lower().startswith(
            prefix_lower
        )
    ]


# ============================================
# Detect completion context
# ============================================

def get_completion_context(
    source,
    line,
    column,
):

    lines = source.splitlines()

    if line < 0 or line >= len(lines):

        return (
            "global",
            None,
            "",
        )

    text = lines[line]

    if column < 0:
        column = 0

    if column > len(text):
        column = len(text)

    before = text[:column]


    # =========================================
    # from ocr import FIND_TEXT,
    # from ocr import FIND_TEXT, CLICK_TEXT,
    # =========================================

    match = re.search(
        r"\bfrom\s+([A-Za-z_]\w*)\s+import\s+"
        r"([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*\s*,?)\s*$",
        before,
    )

    if match:

        return (
            "import",
            match.group(1),
            "",
        )


    # =========================================
    # from ocr import
    # from ocr import F
    # =========================================

    match = re.search(
        r"\bfrom\s+([A-Za-z_]\w*)\s+import"
        r"(?:\s+([A-Za-z_]\w*))?\s*$",
        before,
    )

    if match:

        return (
            "import",
            match.group(1),
            match.group(2) or "",
        )


    # =========================================
    # from
    # from o
    # =========================================

    match = re.search(
        r"\bfrom(?:\s+([A-Za-z_]\w*))?\s*$",
        before,
    )

    if match:

        return (
            "from_module",
            None,
            match.group(1) or "",
        )


    # =========================================
    # import cv2,
    # import cv2, ocr,
    # =========================================

    match = re.search(
        r"\bimport\s+"
        r"([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*\s*,?)\s*$",
        before,
    )

    if match:

        return (
            "import_module",
            None,
            "",
        )


    # =========================================
    # import
    # import o
    # =========================================

    match = re.search(
        r"\bimport(?:\s+([A-Za-z_]\w*))?\s*$",
        before,
    )

    if match:

        return (
            "import_module",
            None,
            match.group(1) or "",
        )

    # Phần +:
    # =========================================
    # Không phải member
    #
    # import cv2.
    # import cv2, ocr.
    # =========================================

    if re.search(
        r"^\s*import\b",
        before,
    ):
        return (
            "import_module",
            None,
            "",
        )

    # =========================================
    # ocr.
    # ocr.F
    # =========================================

    match = re.search(
        r"([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\.(\w*)$",
        before,
    )

    if match:

        return (
            "member",
            match.group(1),
            match.group(2),
        )
    # =========================================
    # Function call
    #
    # add(
    # add(1,
    # add(1, 5
    # add(1, value
    #
    # object.method(
    # ocr.FIND_TEXT(
    # =========================================

    match = re.search(
        r"([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\("
        r"[^()\n]*$",
        before,
    )

    if match:

        function_name = match.group(1)

        # -------------------------------------
        # Text của argument hiện tại
        # -------------------------------------

        argument_text = before[
            match.end():
        ]

        # Nếu có dấu comma, chỉ lấy phần
        # argument hiện tại.
        if "," in argument_text:

            argument_text = argument_text.rsplit(
                ",",
                1,
            )[1]

        argument_text = argument_text.strip()

        # -------------------------------------
        # Nếu đang ở cuối identifier
        #
        # add(1, va
        #             ^^
        #
        # prefix = va
        # -------------------------------------

        prefix_match = re.search(
            r"([A-Za-z_]\w*)$",
            argument_text,
        )

        prefix = (
            prefix_match.group(1)
            if prefix_match
            else ""
        )

        return (
            "call",
            function_name,
            prefix,
        )

    # =========================================
    # Global
    # =========================================

    return (
        "global",
        None,
        "",
    )

def get_imported_modules(
    source,
):
    imported = set()

    for line in source.splitlines():

        line = line.strip()

        # =================================
        # import ...
        # =================================

        match = re.match(
            r"^import\s+(.+)$",
            line,
        )

        if match:

            items = match.group(1).split(",")

            for item in items:

                item = item.strip()

                if not item:
                    continue

                # -------------------------
                # module as alias
                # -------------------------

                match_alias = re.match(
                    r"^([A-Za-z_]\w*)\s+as\s+([A-Za-z_]\w*)$",
                    item,
                )

                if match_alias:

                    module = match_alias.group(1)

                    imported.add(
                        module
                    )

                    continue

                # -------------------------
                # module
                # -------------------------

                match_module = re.match(
                    r"^([A-Za-z_]\w*)$",
                    item,
                )

                if match_module:

                    module = match_module.group(1)

                    imported.add(
                        module
                    )

            continue

        # =================================
        # from module import ...
        # =================================

        match = re.match(
            r"^from\s+([A-Za-z_]\w*)\s+import\b",
            line,
        )

        if match:

            module = match.group(1)

            imported.add(
                module
            )

    return imported

def complete(
    source,
    line,
    column,
):

    context, object_name, prefix = (
        get_completion_context(
            source,
            line,
            column,
        )
    )

    imported_modules = (
        get_imported_modules(
            source
        )
    )

    # =================================
    # Parse
    # =================================

    tree = parse_completion_tree(
        source,
        line,
        column,
    )

    analyzer = CompletionAnalyzer(
        tree,
        imported_modules,
    )


    # =================================
    # From module
    # from
    # from o
    # =================================

    if context == "from_module":

        result = analyzer.find_modules()

        # from cv2 |
        if prefix and source.splitlines()[line][:column].endswith(
            prefix + " "
        ):
            result = [
                item
                for item in result
                if item.get("label") != prefix
            ]

        return filter_items(
            result,
            prefix,
        )

    # =================================
    # Import module
    # import
    # import o
    # =================================

    if context == "import_module":

        result = analyzer.find_modules()

        if prefix and source.splitlines()[line][:column].endswith(prefix + " "):
            result = [
                item for item in result if item.get("label") != prefix
            ]

        return filter_items(
            result,
            prefix,
        )


    # =================================
    # Member
    #
    # ocr.
    # ocr.F
    # =================================

    if context == "member":

        result = analyzer.find_member(
            object_name
        )

        return filter_items(
            result,
            prefix,
        )

    # =================================
    # function call
    # =================================
    
    if context == "call":
        result = analyzer.find_call(object_name)
        return filter_items(result, prefix)


    # =================================
    # Import symbol
    # from ocr import
    # from ocr import F
    # =================================
    
    if context == "import":

        result = analyzer.find_imports(
            object_name
        )

        # from cv2 import FIND_IMG |
        if prefix and source.splitlines()[line][:column].endswith(
            prefix + " "
        ):
            result = [
                item
                for item in result
                if item.get("label") != prefix
            ]

        return filter_items(
            result,
            prefix,
        )

    # =================================
    # Global
    # =================================

    result = []

    result.extend(
        analyzer.global_symbols()
    )

    result.extend(
        analyzer.builtin_symbols()
    )

    result.extend(
        analyzer.keyword_symbols()
    )

    result.extend(
        analyzer.constant_symbols()
    )

    return result

def parse_completion_tree(
    source,
    line,
    column,
):
    try:
        tokens = Scanner(
            source
        ).scan()

        return Parser(
            tokens
        ).parse()

    except Exception:

        # =====================================
        # Incomplete expression sau cursor
        #
        # Ví dụ:
        # import cv2
        # cv2.
        #
        # → phân tích phần trước statement
        # =====================================

        lines = source.splitlines(
            keepends=True
        )

        if line >= len(lines):
            return None

        # Giữ toàn bộ source trước dòng hiện tại
        before = "".join(
            lines[:line]
        )

        # Chỉ lấy phần trước expression hiện tại
        current = lines[line][:column]

        # Nếu current đang là member expression:
        #
        # cv2.
        # img.foo.
        #
        # thì bỏ expression đó.
        #
        # Tạm thời lấy từ đầu dòng.
        #
        # Quan trọng: đây chỉ là fallback
        # khi parse toàn bộ source đã fail.
        analysis_source = before

        if analysis_source.strip():

            try:

                tokens = Scanner(
                    analysis_source
                ).scan()

                return Parser(
                    tokens
                ).parse()

            except Exception:
                pass

        return None


# ============================================
# Main
# ============================================

def main():

    if len(sys.argv) < 3:

        print(
            json.dumps(
                {
                    "context": "global",
                    "symbols": [],
                },
                ensure_ascii=False,
            )
        )

    try:

        line = int(
            sys.argv[1]
        )

        column = int(
            sys.argv[2]
        )

        source = sys.stdin.read()
        result = complete(source=source,line=line,column=column)

        print(json.dumps(result, ensure_ascii=False))

    except Exception as error:
        # traceback.print_exc(file=sys.stderr)

        print(
            json.dumps(
                {
                    "error": str(error)
                },
                ensure_ascii=False,
            )
        )

if __name__ == "__main__":
    main()