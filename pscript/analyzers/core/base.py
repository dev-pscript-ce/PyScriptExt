import sys
sys.dont_write_bytecode=True

class AnalyzerBase:
    # =====================================
    # AST Visitor
    # =====================================

    def visit(self, node):

        if node is None:
            return

        # =================================
        # List / Tuple
        # =================================

        if isinstance(node, (list, tuple)):

            for item in node:
                self.visit(item)

            return

        # =================================
        # AST dispatcher
        # =================================

        method_name = (
            "visit_"
            + node.__class__.__name__
        )

        method = getattr(
            self,
            method_name,
            None,
        )

        if method is not None:
            return method(node)

        # =================================
        # Generic traversal
        # =================================

        if hasattr(node, "__dict__"):

            for name, value in vars(node).items():

                # Metadata / token
                if (
                    name == "token"
                    or name.endswith("_token")
                ):
                    continue

                self.visit(value)

        return