import sys
sys.dont_write_bytecode = True

from pscript.asts.expressions import Variable
from pscript.analyzers.core.symbols import Symbols

class AnalyzerAssign:

    def visit_Assign(
            self,
            node,
        ):
    
            # RHS trước
            value_info = self.visit(
                node.value
            )
    
            # Sau đó mới define target
            if node.operator == "=":
    
                if isinstance(
                    node.target,
                    Variable,
                ):
    
                    self.scopes.define(
                        node.target.name,
                        Symbols(
                            name=node.target.name,
                            kind="variable",
                            node=node.target,
                            data=value_info,
                        ),
                    )
                    self.add_semantic_token(
                        node.target,
                        "variable",
                    )
    
                return
    
            # +=, -= ...
            self.visit(
                node.target
            )

class AnalyzerForStatement:

    def visit_ForStatement(
        self,
        node,
    ):

        # =================================
        # Iterable
        # =================================

        self.visit(
            node.iterable
        )

        # =================================
        # For scope
        # =================================

        self.scopes.enter_scope(
            name=f"for:{node.name}",
            kind="for",
        )

        try:

            # -----------------------------
            # Loop variable
            # -----------------------------

            self.scopes.define(
                node.name,
                Symbols(
                    name=node.name,
                    kind="variable",
                    node=node,
                ),
            )

            # -----------------------------
            # Body
            # -----------------------------

            self.visit(
                node.block
            )

        finally:

            self.scopes.exit_scope()

class AnalyzerReturnStatement:

    def visit_ReturnStatement(
        self,
        node,
    ):

        if node.value is not None:
            return self.visit(
                node.value
            )

        return None

class AnalyzerStmts(
    AnalyzerAssign,
    AnalyzerForStatement,
    AnalyzerReturnStatement,
):
    pass