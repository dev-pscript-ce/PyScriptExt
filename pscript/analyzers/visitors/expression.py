import sys
sys.dont_write_bytecode = True

from pscript.tokens.semantic_tokens_type import SEMANTIC_TOKEN_KINDS
from pscript.analyzers.core.definitions import BUILTINS
from pscript.asts.expressions import (
    Variable,
    MemberAccess
)
from pscript.analyzers.core.symbols import Symbols

class AnalyzerVariable :

    def visit_Variable(
        self,
        node,
    ):

        symbol = self.resolve_symbol(
            node.name,
        )

        if symbol is not None:

            token_type = SEMANTIC_TOKEN_KINDS.get(
                symbol.kind,
            )

            if token_type is not None:
                self.add_semantic_token(
                    node,
                    token_type,
                )

            return symbol

        # =========================================
        # Builtin method
        # =========================================

        builtin_methods = BUILTINS.get(
            "methods",
            {},
        )

        if node.name in builtin_methods:
            return {
                "kind": "builtin_method",
                "name": node.name,
                "data": builtin_methods[node.name],
            }

        # =========================================
        # Builtin object
        # =========================================

        builtin_objects = BUILTINS.get(
            "objects",
            {},
        )

        if node.name in builtin_objects:
            return {
                "kind": "builtin_object",
                "name": node.name,
                "data": builtin_objects[node.name],
            }

        # =========================================
        # Undefined
        # =========================================

        self.add_error(
            node=node,
            message=(
                f'Name "{node.name}" '
                "is not defined"
            ),
            code="PSCRIPT_NAME_NOT_DEFINED",
        )

        return None

class AnalyzerBinaryExpr:

    def visit_BinaryExpr(
        self,
        node,
    ):

        left = self.visit(
            node.left
        )

        right = self.visit(
            node.right
        )

        return {
            "kind": "binary",
            "op": node.op,
            "left": left,
            "right": right,
        }
    
class AnalyzerMemberAccess:
    
    def visit_MemberAccess(
            self,
            node,
        ):
    
            # =========================================
            # Builtin object
            # print.Y(...)
            # print.R(...)
            # print.G(...)
            # =========================================
            
    
            if isinstance(
                node.obj,
                Variable,
            ):
    
                builtin_objects = (
                    BUILTINS.get(
                        "objects",
                        {},
                    )
                )
    
                if node.obj.name in builtin_objects:
    
                    return
    
            # =========================================
            # Visit object first
            # =========================================
    
            self.visit(
                node.obj
            )
    
            # =========================================
            # Resolve member
            # =========================================
    
            member_info = (
                self.resolve_member_chain(
                    node
                )
            )
    
            if member_info is None:
                return None
    
            # =========================================
            # User-defined method
            # =========================================
    
            if (
                member_info.get("kind")
                == "method"
            ):
    
                definition = (
                    member_info.get(
                        "definition"
                    )
                )
    
                if definition is not None:
    
                    self.add_semantic_token(
                        node,
                        SEMANTIC_TOKEN_KINDS[
                            "user_defined_method"
                        ],
                    )
    
            return member_info

    def member_chain_name(
            self,
            node,
        ):
        
            parts = []
    
            current = node
    
            visited = set()
            
            while True:
    
                current_id = id(current)
    
                if current_id in visited:
                    return ""
    
                visited.add(current_id)
    
                # =================================
                # Variable
                # =================================
    
                if isinstance(
                    current,
                    Variable,
                ):
    
                    parts.append(
                        current.name
                    )
    
                    break
    
                # =================================
                # MemberAccess
                # =================================
                
    
                if isinstance(
                    current,
                    MemberAccess,
                ):
    
                    parts.append(
                        current.member
                    )
    
                    current = current.obj
    
                    continue
    
                return ""
    
            parts.reverse()
    
            return ".".join(parts)
    
    # def get_call_name(
    #     self,
    #     node,
    # ):
        
    #     callee = node.callee

    #     # =================================
    #     # foo()
    #     # =================================

    #     if isinstance(
    #         callee,
    #         Variable,
    #     ):

    #         return callee.name

    #     # =================================
    #     # module.method()
    #     # ocr.click_text()
    #     # cv2.find_img()
    #     # =================================

    #     if isinstance(
    #         callee,
    #         MemberAccess,
    #     ):

    #         if isinstance(
    #             callee.obj,
    #             Variable,
    #         ):

    #             return (
    #                 f"{callee.obj.name}."
    #                 f"{callee.member}"
    #             )

    #     return None

    def get_call_name(self, node):
        return self.member_chain_name(node.callee)

class AnalyzerWalrusExpr:

    def visit_WalrusExpr(self, node):
    
            # RHS phải được phân tích trước
            self.visit(node.value)
    
            if not isinstance(node.target, Variable):
                self.error(
                    node.target,
                    "Walrus target must be a variable",
                )
                return
    
            self.scopes.define(
                node.target.name,
                Symbols(
                    name=node.target.name,
                    kind="variable",
                    node=node.target,
                ),
            )

class AnalyzerExprs(
    AnalyzerVariable,
    AnalyzerMemberAccess,
    AnalyzerBinaryExpr,
    AnalyzerWalrusExpr,
):
    pass
