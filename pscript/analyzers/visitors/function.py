import sys
sys.dont_write_bytecode = True

from pscript.asts.expressions import (
    Variable,
    MemberAccess,
)

from pscript.asts.arguments import (
    StarArgument,
    NamedArgument,
    KwStarArgument
)

from pscript.analyzers.core.definitions import BUILTINS

from pscript.analyzers.core.symbols import Symbols
from pscript.tokens.semantic_tokens_type import SEMANTIC_TOKEN_KINDS

class AnalyzerFunctionCall:

    def visit_FunctionCall(
        self,
        node,
    ):

        callee = node.callee

        self.visit(callee) # +new

        # =================================
        # Direct function / builtin
        # =================================

        if isinstance(
            callee,
            Variable,
        ):

            name = callee.name

            # Class constructor
            symbol = self.scopes.resolve(name)

            if (
                symbol is not None
                and symbol.kind == "user_defined_class"
            ):
                
                return{
                    "kind": "instance",
                    "class": symbol,
                }

            
            # -----------------------------
            # Builtin object
            # -----------------------------

            builtin_objects = (
                BUILTINS.get(
                    "objects",
                    {},
                )
            )

            builtin = builtin_objects.get(name)

            if builtin is not None:

                # Object có thể gọi trực tiếp
                if (
                    isinstance(builtin, dict)
                    and builtin.get(
                        "callable",
                        False,
                    )
                ):

                    self.validate_FunctionCall(
                        node
                    )

                else:

                    self.add_error(
                        node=callee,

                        message=(
                            f'Builtin object "{name}" '
                            f'requires a member'
                        ),

                        code=(
                            "PSCRIPT_OBJECT_NOT_CALLABLE"
                        ),
                    )

            else:

                self.validate_FunctionCall(
                    node
                )


        # =================================
        # Member access
        # =================================

        elif isinstance(
            callee,
            MemberAccess,
        ):

            self.validate_MemberAccess(
                node
            )

        # =================================
        # Other callable expression
        # =================================

        else:

            self.visit(
                callee
            )

        # =================================
        # Arguments
        # =================================

        for arg in node.args:

            if isinstance(
                arg,
                NamedArgument,
            ):

                self.visit(
                    arg.value
                )

            elif isinstance(
                arg,
                StarArgument,
            ):

                self.visit(
                    arg.value
                )

            elif isinstance(
                arg,
                KwStarArgument,
            ):

                self.visit(
                    arg.value
                )

            else:

                self.visit(
                    arg
                )

class AnalyzerFunctionDef:

    def visit_FunctionDef(
            self,
            node,
        ):
    
            symbol = Symbols(
                name=node.name,
                kind="user_defined_function",
                node=node,
                data={
                    "params": node.params,
                },
            )
    
            # Define function
            self.scopes.define(
                node.name,
                symbol,
            )
    
            # Highlight function name
            if self.current_class is not None:
    
                token_type = (
                    SEMANTIC_TOKEN_KINDS[
                        "user_defined_method"
                    ]
                )
    
                self.current_class.data[
                    "methods"
                ][node.name] = symbol
            else:
    
                token_type = (
                    SEMANTIC_TOKEN_KINDS[
                        "user_defined_function"
                    ]
                )
    
            self.add_semantic_token(
                node,
                token_type,
            )
    
            # Function scope
            self.scopes.enter_scope(
                node.name,
                kind="user_defined_function",
            )
    
            try:
    
                # Parameters
                for param in node.params:
    
                    self.scopes.define(
                        param.name,
                        Symbols(
                            name=param.name,
                            kind="params",
                            node=param,
                        ),
                    )
    
                    self.add_semantic_token(
                        param,
                        SEMANTIC_TOKEN_KINDS[
                            "params"
                        ],
                    )
    
                self.visit(
                    node.body
                )
    
            finally:
    
                self.scopes.exit_scope()

class AnalyzerLambdaExpr:

    def visit_LambdaExpr(
        self,
        node,
    ):

        self.scopes.enter_scope(
            name="<lambda>",
            kind="func",
        )

        try:

            for param in node.params:

                self.scopes.define(
                    param.name,
                    Symbols(
                        name=param.name,
                        kind="params",
                        node=param,
                    ),
                )

            self.visit(node.body)

        finally:

            self.scopes.exit_scope()

class AnalyzerFunctions(
    AnalyzerFunctionCall,
    AnalyzerFunctionDef,
    AnalyzerLambdaExpr,
):
    pass