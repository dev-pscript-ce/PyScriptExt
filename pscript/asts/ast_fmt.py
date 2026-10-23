import sys
sys.dont_write_bytecode = True

# from dsl_scan.asts.literals import FStringText

class ASTFormatter:

    def format(self, node):

        method = getattr(
            self,
            f"visit_{type(node).__name__}",
            self.generic
        )

        return method(node)

    def generic(self, node):
        return type(node).__name__

    def visit_Number(self, node):
        return str(node.value)

    def visit_String(self, node):
        return repr(node.value)

    def visit_Variable(self, node):
        return node.name

    def visit_BinaryExpr(self, node):
        return (
            f"({self.format(node.left)} "
            f"{node.op} "
            f"{self.format(node.right)})"
        )

    def visit_UnaryExpr(self, node):
        return f"{node.op}{self.format(node.expr)}"
    
    def visit_TernaryExpr(self, node):
        return (
            f"({self.format(node.condition)})"
            f" ? {self.format(node.then_expr)}"
            f" : {self.format(node.else_expr)}"
        )
    
    def visit_UpdateExpr(self, node):

        expr = self.format(node.target)

        if node.prefix:
            return f"{node.op}{expr}"

        return f"{expr}{node.op}"

    def visit_FunctionCall(self, node):
        args = ", ".join(
            self.format(a)
            for a in node.args
        )
        return f"{self.format(node.callee)}({args})"

    def visit_MemberAccess(self, node):
        return (
            f"{self.format(node.obj)}."
            f"{node.member}"
        )
    
    def visit_WalrusExpr(self, node):
        return (
            f"({self.format(node.target)}) := "
            f"{self.format(node.value)}"
        )
    
    def visit_FStringText(self, node):
        return node.value

    def visit_FString(self, node):

        return '"' + "".join(
            self.format(part)
            for part in node.parts
        ) + '"'

    # def visit_FString(self, node):

    #     out = []

    #     for part in node.parts:

    #         if isinstance(part, FStringText):
    #             out.append(part.value)
    #         else:
    #             out.append("${")
    #             out.append(self.format(part))
    #             out.append("}")

    #     return '"' + "".join(out) + '"'