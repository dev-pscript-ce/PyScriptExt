import sys
sys.dont_write_bytecode = True

from pscript.analyzers.core.definitions import MODULES
from pscript.analyzers.core.symbols import Symbols

class AnalyzerImport:
    # =====================================
    # import ocr
    #
    # import ocr as screen
    # =====================================
    def visit_Import(
            self,
            node,
        ):
    
            for (
                module_name,
                alias,
                is_file,
            ) in node.imports:
    
                # =================================
                # Module tồn tại?
                # =================================
    
                if (
                    not is_file
                    and module_name not in MODULES
                ):
    
                    self.add_error(
                        node=node,
    
                        message=(
                            f'No module named '
                            f'"{module_name}"'
                        ),
    
                        code=(
                            "PSCRIPT_MODULE_NOT_FOUND"
                        ),
                    )
    
                    continue
    
                # =================================
                # import registry
                # =================================
    
                self.imported_modules.add(
                    module_name
                )
    
                # =================================
                # Symbol name
                # import ocr
                #     -> ocr
                # import ocr as screen
                #     -> screen
                # =================================
    
                symbol_name = (
                    alias
                    if alias
                    else module_name
                )
    
                self.scopes.define(
                    symbol_name,
    
                    Symbols(
                        name=symbol_name,
                        kind="module",
                        node=node,
                    ),
                )
                # =================================
                # Alias
                # =================================
    
                if alias:
    
                    self.module_aliases[
                        alias
                    ] = module_name

class AnalyzerFromImport:
    # =====================================
    # from ocr import find_text
    # =====================================

    def visit_FromImport(
        self,
        node,
    ):

        module_name = node.module

        # =================================
        # Module
        # =================================

        module = MODULES.get(
            module_name,
        )

        if module is None:

            self.add_error(
                node=node,

                message=(
                    f'No module named '
                    f'"{module_name}"'
                ),

                code=(
                    "PSCRIPT_MODULE_NOT_FOUND"
                ),
            )

            return

        # =================================
        # Ghi nhận module đã import
        # =================================

        self.imported_modules.add(
            module_name,
        )

        # =================================
        # Methods
        # =================================

        methods = module.get(
            "methods",
            {},
        )

        # =================================
        # from xxx import *
        # =================================

        if (
            len(node.names) == 1
            and node.names[0][0] == "*"
        ):

            for name, method in methods.items():

                if name.startswith("_"):
                    continue

                self.scopes.define(
                    name,

                    Symbols(
                        name=name,
                        kind="import",
                        node=node,
                        data=method,
                    ),
                )

            return

        # =================================
        # from xxx import a, b as c
        # =================================

        for name, alias in node.names:

            # -----------------------------
            # Kiểm tra member
            # -----------------------------

            method = methods.get(
                name,
            )

            if method is None:

                self.add_error(
                    node=node,

                    message=(
                        f'Cannot import name '
                        f'"{name}" '
                        f'from "{module_name}"'
                    ),

                    code=(
                        "PSCRIPT_IMPORT_NAME_NOT_FOUND"
                    ),
                )

                continue

            # -----------------------------
            # Tên trong scope
            # -----------------------------

            symbol_name = (
                alias
                if alias
                else name
            )

            self.scopes.define(
                symbol_name,

                Symbols(
                    name=symbol_name,
                    kind="import",
                    node=node,
                    data=method,
                ),
            )

            # -----------------------------
            # Alias
            # -----------------------------

            if alias:

                self.module_aliases[
                    alias
                ] = (
                    f"{module_name}.{name}"
                )


class AnalyzerImports(
    AnalyzerImport,
    AnalyzerFromImport,
):
    pass