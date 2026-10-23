import sys
sys.dont_write_bytecode = True

from.base import Node,ExprNode

class Variable(ExprNode):
    def __init__(self,name:str,token=None):
        super().__init__(token)
        self.name = name

    # def __repr__(self):
    #     return f"Variable({self.name})"
    
class BinaryExpr(ExprNode):
    def __init__(self,left:ExprNode, op:str, right:ExprNode,token=None):

        super().__init__(token)
        
        self.left = left
        self.op = op
        self.right = right
        
    # def __repr__(self):
    #     return f"({self.left} {self.op} {self.right})"
    
class UnaryExpr(ExprNode):
    def __init__(self, op:str, expr:ExprNode):
        self.op = op
        self.expr = expr

class TernaryExpr(ExprNode):
    def __init__(
            self, 
            condition:ExprNode, 
            then_expr:ExprNode, 
            else_expr:ExprNode
        ):
        self.condition = condition
        self.then_expr = then_expr
        self.else_expr = else_expr

    
class MemberAccess(ExprNode):

    def __init__(self, obj:ExprNode, member:str,token=None):
        
        super().__init__(token)
        self.obj = obj
        self.member = member

class RangeExpression(ExprNode):

    def __init__(self, start:ExprNode, end:ExprNode):
        self.start = start
        self.end = end

    # def __repr__(self):
    #     return (
    #         f"Range({self.start}..{self.end})"
    #     )
    
class IndexExpr(ExprNode):

    def __init__(self, target:ExprNode, index:ExprNode):

        self.target = target
        self.index = index

class AssignIndex(Node):

    def __init__(
            self, 
            target:ExprNode,
            index:ExprNode,
            value:ExprNode
        ):

        self.target = target
        self.index = index
        self.value = value

class SliceExpr(ExprNode):

    def __init__(
        self,
        target:ExprNode,
        start:ExprNode|None,
        stop:ExprNode|None,
        step:ExprNode|None,
    ):
        self.target = target
        self.start = start
        self.stop = stop
        self.step = step

class UpdateExpr(ExprNode):
    def __init__(self, target:ExprNode, op:str, prefix:bool):
        
        self.target = target
        self.op =op
        self.prefix=prefix

class WalrusExpr(ExprNode):
    def __init__(self, target:ExprNode, value:ExprNode):
        self.target = target
        self.value = value


