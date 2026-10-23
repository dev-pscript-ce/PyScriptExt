import sys 
sys.dont_write_bytecode = True

from pscript.analyzers.core.definitions import (
    MODULES,
    BUILTINS
)

from pscript.analyzers.core import Symbols

from pscript.asts.expressions import (
    MemberAccess,
    Variable
)

from pscript.asts.functions import (
    FunctionCall
)

from pscript.asts.classes import (
    SuperExpr,
)

class Resolver:

    def resolve_symbol(self, name):
        return self.scopes.resolve(name)

    def resolve_diagnostic_path(
        self,
        path,
    ):

        if not isinstance(path, str):
            return None

        path = path.strip()

        if not path:
            return None

        parts = path.split(".")
        root = parts[0]

        # =================================
        # User-defined symbol
        # =================================

        if len(parts) == 1:

            symbol = self.scopes.resolve(
                root
            )

            if symbol is not None:
                return symbol

        
        # =================================
        # Builtin object
        # =================================

        builtin = (
            BUILTINS
            .get("objects", {})
            .get(root)
        )

        if isinstance(builtin, dict):

            definition = builtin

            for part in parts[1:]:

                if not isinstance(definition, dict):
                    return None

                methods = definition.get(
                    "methods", {}
                )

                if not isinstance(methods, dict):
                    return None

                definition = methods.get(part)

                if definition is None:
                    return None

            return definition


        # =================================
        # Imported module
        # =================================

        module_name = (
            self.module_aliases
            .get(root, root)
        )

        if module_name != root:

            path = ".".join(
                [
                    module_name,
                    *parts[1:],
                ]
            )

        return resolve_path(
            path=path,
            imported_modules=(
                self.imported_modules
            ),
        )

    def resolve_member_chain(
        self,
        node,
    ):

        # =================================
        # super().method
        # =================================

        if isinstance(
            node,
            MemberAccess,
        ):

            obj = node.obj

            if (
                isinstance(
                    obj,
                    FunctionCall,
                )
                and isinstance(
                    obj.callee,
                    SuperExpr,
                )
            ):

                super_info = self.visit(
                    obj.callee
                )

                if super_info is not None:

                    base = super_info.get(
                        "base"
                    )

                    method = (
                        self.resolve_class_method(
                            base,
                            node.member,
                        )
                    )

                    if method is not None:

                        return {
                            "kind": "method",
                            "name": (
                                f"super().{node.member}"
                            ),
                            "definition": method,
                        }

            # =================================
            # super.method
            # =================================

            if isinstance(
                obj,
                SuperExpr,
            ):

                super_info = self.visit(
                    obj
                )

                if super_info is not None:

                    base = super_info.get(
                        "base"
                    )
                    method = (
                        self.resolve_class_method(
                            base,
                            node.member,
                        )
                    )

                    if method is not None:

                        return {
                            "kind": "method",
                            "name": (
                                f"super.{node.member}"
                            ),
                            "definition": method,
                        }

        # =================================
        # Path
        # =================================

        path = self.member_chain_name(
            node
        )

        if not path:
            return None

        # =================================
        # Instance / variable
        # =================================

        if isinstance(
            node,
            MemberAccess,
        ):

            obj = node.obj

            if isinstance(
                obj,
                Variable,
            ):

                symbol = (
                    self.scopes.resolve(
                        obj.name
                    )
                )

                if symbol is not None:

                    data = symbol.data

                    if (
                        isinstance(data, dict)
                        and data.get("kind")
                        == "instance"
                    ):

                        class_symbol = (
                            data.get("class")
                        )

                        if not isinstance(
                            class_symbol,
                            Symbols,
                        ):
                            return None

                        method = (
                            self.resolve_class_method(
                                class_symbol,
                                node.member,
                            )
                        )

                        if method is not None:

                            return {
                                "kind": "method",
                                "name": path,
                                "definition": method,
                            }

                        self.add_error(
                            node=node,
                            message=(
                                f'Class '
                                f'"{class_symbol.name}" '
                                f'has no member '
                                f'"{node.member}"'
                            ),
                            code=(
                                "PSCRIPT_MEMBER_NOT_FOUND"
                            ),
                        )

                        return None

        # =================================
        # Builtin / module
        # =================================

        definition = (
            self.resolve_diagnostic_path(
                path
            )
        )

        if definition is None:
            return None

        return {
            "kind": (
                "method"
                if "parameters" in definition
                else "object"
            ),
            "name": path,
            "definition": definition,
        }

    def resolve_class_method(
        self,
        class_symbol,
        method_name,
    ):

        if not isinstance(
            class_symbol,
            Symbols,
        ):
            return None

        methods = (
            class_symbol.data.get(
                "methods",
                {},
            )
        )

        # =================================
        # Method của chính class
        # =================================

        method = methods.get(
            method_name
        )

        if method is not None:
            return method

        # =================================
        # Base classes
        # =================================

        for base_symbol in (
            class_symbol.data.get(
                "bases",
                [],
            )
        ):

            if not isinstance(
                base_symbol,
                Symbols,
            ):
                continue

            method = (
                self.resolve_class_method(
                    base_symbol,
                    method_name,
                )
            )

            if method is not None:
                return method

        return None
    

def resolve_path(
    path,
    imported_modules=None,
):

    # =================================
    # Builtin
    # =================================

    result = resolve_builtin_path(
        path=path,
    )

    if result is not None:
        return result

    # =================================
    # Module
    # =================================

    result = resolve_module_path(
        path=path,
        imported_modules=(
            imported_modules
            or set()
        ),
    )

    if result is not None:
        return result

    return None

# Module resolver

def resolve_module_path(path,imported_modules):
    
    if not isinstance(path,str):
        return None

    path = path.strip()

    if not path:
        return None

    parts = path.split(".")

    module_name = parts[0]
    module = MODULES.get(module_name)

    if module is None:
        return None

    if module_name not in imported_modules:
        return None 

    current = module

    for part in parts[1:]:
        if not isinstance(current,dict):
            return None
        methods = current.get("methods",{})

        current = methods.get(part)

        if current is None:
            return None
    return current

# =========================================
# Built-in resolver
# =========================================

def resolve_builtin_path(
    path,
):
    """
    Resolve một builtin path từ BUILTINS.

    Hỗ trợ:

        printl
        print
        print.G
        print.error
        print.Y
        print.Y.u
        ansi
        ansi.R
        ansi.R.u

    Trả về metadata node tương ứng.
    Nếu không tìm thấy -> None.
    """

    if not isinstance(
        path,
        str,
    ):
        return None

    path = path.strip()

    if not path:
        return None

    parts = path.split(".")

    # =========================================
    # Global builtin method
    # =========================================

    if len(parts) == 1:

        name = parts[0]

        methods = BUILTINS.get(
            "methods",
            {},
        )

        method = methods.get(
            name,
        )

        if method is not None:
            return method

    # =========================================
    # Built-in object
    # =========================================

    objects = BUILTINS.get(
        "objects",
        {},
    )

    current = objects.get(
        parts[0],
    )

    if current is None:
        return None

    # =========================================
    # Nested members
    # =========================================

    for part in parts[1:]:

        if not isinstance(
            current,
            dict,
        ):
            return None

        methods = current.get(
            "methods",
            {},
        )

        current = methods.get(
            part,
        )

        if current is None:
            return None

    return current

def resolve_namespace(
    path,
    imported_modules,
    module_aliases=None,
):

    # =========================================
    # Built-in namespace
    # =========================================

    result = resolve_builtin_namespace(
        path,
    )

    if result is not None:
        return result

    # =========================================
    # Module namespace
    # =========================================

    result = resolve_module_namespace(
        path,
        imported_modules,
        module_aliases,
    )

    if result is not None:
        return result

    return None

def resolve_module_namespace(
    path,
    imported_modules,
    module_aliases=None,
):
    """
    Resolve module namespace.

    Ví dụ:

        ocr
        cv2
        sdt

    Và alias:

        import ocr as x
        x
    """

    if not isinstance(
        path,
        str,
    ):
        return None

    path = path.strip()

    if not path:
        return None

    parts = path.split(".")

    # =========================================
    # Root module
    # =========================================

    root = parts[0]

    if module_aliases is not None:

        module_name = (
            module_aliases.get(
                root,
                root,
            )
        )

    else:

        module_name = root

    # =========================================
    # Module definition
    # =========================================

    module = MODULES.get(
        module_name,
    )

    if module is None:
        return None

    # =========================================
    # Module phải được import
    # =========================================

    if (
        module_name
        not in imported_modules
    ):
        return None

    current = module

    # =========================================
    # Nested member
    #
    # ocr.find_text
    # =========================================

    for part in parts[1:]:

        if not isinstance(
            current,
            dict,
        ):
            return None

        methods = current.get(
            "methods",
            {},
        )

        current = methods.get(
            part,
        )

        if current is None:
            return None

    return current

# =========================================
# Built-in namespace resolver
# =========================================

def resolve_builtin_namespace(
    path,
):
    """
    Resolve builtin object/namespace.

    Ví dụ:

        print
        print.Y
        ansi
        ansi.R

    Dùng cho Completion.
    """

    if not isinstance(
        path,
        str,
    ):
        return None

    path = path.strip()

    if not path:
        return None

    parts = path.split(".")

    objects = BUILTINS.get(
        "objects",
        {},
    )

    current = objects.get(
        parts[0],
    )

    if current is None:
        return None

    for part in parts[1:]:

        if not isinstance(
            current,
            dict,
        ):
            return None

        methods = current.get(
            "methods",
            {},
        )

        current = methods.get(
            part,
        )

        if current is None:
            return None

    return current