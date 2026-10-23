import sys
sys.dont_write_bytecode = True

from pscript.asts.literals import (
    Number,
    String
)

from pscript.asts.expressions import (
    BinaryExpr,
    UnaryExpr,
    Variable,
    MemberAccess
)
from pscript.asts.statements import (
    Assign,
    Block
)
from pscript.asts.functions import FunctionCall

from pscript.asts.program import Program
from pscript.asts.imports import Import


class ASTPrinter:
    def print(self, node):
        self.execute(node)

    def execute(self, node, prefix="", last=True):
        if node is None:
            return
        
        branch = "└── " if last else "├── "

        print(prefix + branch + self.lable(node))

        children = self.children(node)

        for i, child in enumerate(children):

            self.execute(
                child,
                prefix + ("    " if last else "│   "),
                i == len(children) - 1
            )

    def lable(self, node):
        if isinstance(node, Number):
            return f"Number({node.value})"
        if isinstance(node, String):
            return f"String({node.value})"
        if isinstance(node, Variable):
            return f"Variable({node.target})"
        if isinstance(node, MemberAccess):
            return f"MemberAccess({node.member})"
        
        return type(node).__name__
    
    def children(self,node):
        if isinstance(node, Assign):
            return [
                node.target,
                node.value
            ]
        
        if isinstance(node, Block):
            return node.body
        
        if isinstance(node, FunctionCall):
            return [
                node.callee,
                *node.args
            ]
        if isinstance(node, BinaryExpr):
            return [
                node.left,
                node.right
            ]
        
        if isinstance(node, UnaryExpr):
            return [
                node.expr
            ]
        
        if isinstance(node, MemberAccess):
            return [node.obj]
        
        if isinstance(node, Import):

            return [node.module,node.alias]
        
        
        if isinstance(node, Program):
            return node.body
        
        return []
        
