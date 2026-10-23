import sys
sys.dont_write_bytecode = True

from pscript.analyzers.core.symbols import Symbols
from pscript.asts.expressions import Variable
from pscript.tokens.semantic_tokens_type import SEMANTIC_TOKEN_KINDS

class AnalyzerClassDef:

    def visit_ClassDef(
        self,
        node,
    ):

        symbol = Symbols(
            name=node.name,
            kind="user_defined_class",
            node=node,
            data={
                "bases": [],
                "methods":{},
            },
        )

        # Define class
        self.scopes.define(
            node.name,
            symbol,
        )

        for base_node in node.bases:

            if isinstance(
                base_node,
                Variable,
            ):

                base_symbol = self.scopes.resolve(
                    base_node.name
                )

                if (
                    base_symbol is not None
                    and base_symbol.kind
                    == "user_defined_class"
                ):
                    symbol.data["bases"].append(
                        base_symbol
                    )

        # Highlight class name
        self.add_semantic_token(
            node,
            SEMANTIC_TOKEN_KINDS[
                "user_defined_class"
            ],
        )

        previous_class = self.current_class
        self.current_class = symbol

        self.scopes.enter_scope(
            node.name,
            kind="class",
        )

        try:

            self.visit(
                node.body
            )

        finally:

            self.scopes.exit_scope()

            self.current_class = previous_class

class AnalyzerSuperExpr:

    def visit_SuperExpr(
            self,
            node,
        ):
    
            if self.current_class is None:
    
                self.add_error(
                    node=node,
                    message=(
                        '"super" can only be used '
                        'inside a class'
                    ),
                    code=(
                        "PSCRIPT_SUPER_OUTSIDE_CLASS"
                    ),
                )
    
                return None
    
            bases = (
                self.current_class.data.get(
                    "bases",
                    []
                )
            )
    
            if not bases:
    
                self.add_error(
                    node=node,
                    message=(
                        f'Class '
                        f'"{self.current_class.name}" '
                        f'has no base class'
                    ),
                    code=(
                        "PSCRIPT_NO_BASE_CLASS"
                    ),
                )
    
                return None
    
            return {
                "kind": "super",
                "class": self.current_class,
                "base": bases[0],
            }

class AnalyzerClasses(
    AnalyzerClassDef,
    AnalyzerSuperExpr,
):
    pass