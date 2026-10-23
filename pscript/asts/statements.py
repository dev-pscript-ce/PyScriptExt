import sys
sys.dont_write_bytecode = True
from .base import StatementNode,ExprNode

class ExpressionStatement(StatementNode):
    def __init__(self, expr:ExprNode):
        self.expr = expr

    def __repr__(self):
        return f"ExpressionStatement({self.expr!r})" 

class Assign(StatementNode):
    def __init__(self, target:ExprNode, operator:str,value:ExprNode):
        self.target = target
        self.operator = operator
        self.value = value

    def __repr__(self):
        return (
            f"Assign("
            f"{self.target!r}={self.value!r})"
        )

    
class Block(StatementNode):
    def __init__(self, body:list[StatementNode]):
        self.body = body

    def __rep__(self):
        return f"Block({self.body})"
    
class IfStatement(StatementNode):

    def __init__(
        self,
        condition:ExprNode,
        then_block:Block,
        elif_blocks:list[tuple[ExprNode,Block]]|None=None,
        else_block:Block|None=None
    ):
        self.condition = condition
        self.then_block = then_block
        self.elif_blocks = (
            elif_blocks 
            if elif_blocks is not None 
            else []
            )
        self.else_block = else_block

    def __repr__(self):
        return (
            f"IfStatement("
            f"{self.condition}, "
            f"{self.then_block}, "
            f"{self.elif_blocks}, "
            f"{self.else_block})"
        )
    
class WhileStatement(StatementNode):
    def __init__(self, condition:ExprNode, block:Block):
        self.condition = condition
        self.block =  block

    # def __repr__(self):
    #     return f"While({self.condition}, {self.block})"
    
class ForStatement(StatementNode):
    def __init__(self, name:str, iterable:ExprNode, block:Block):
        self.name = name
        self.iterable = iterable
        self.block = block

    def __repr__(self):
        return (
            f"For({self.name},"
            f"({self.iterable})"
        )
    
class BreakStatement(StatementNode):
    def __repr__(self):
        return "Break()"
    
class ContinueStatement(StatementNode):
    def __repr__(self):
        return "Continue()"
    
class ReturnStatement(StatementNode):
    def __init__(self, value:ExprNode|None,token=None):
        super().__init__(token)
        self.value = value

    def __repr__(self):
        return f"Return({self.value})"

class CaseClause(StatementNode):
    def __init__(self,values:list[ExprNode],block:Block):
        self.values = values
        self.block = block
    def __repr__(self):
        return (
            f"CaseClause({self.values}, {self.block})"
        )

class SwitchStatement(StatementNode):
    def __init__(
            self, 
            expr:ExprNode,
            cases:list[CaseClause],
            default_block: Block| None = None
        ):
        self.expr = expr
        self.cases = cases
        self.default_block = default_block
    def __repr__(self):
        return (
            f"SwitchStatement({self.expr}, {self.cases}, {self.default_block})"
        )

class CatchClause(StatementNode):
    def __init__(
            self, 
            exception_type:ExprNode|None, 
            name: str | None,
            block: Block,
        ):
            self.exception_type = exception_type
            self.name = name
            self.block = block

    def __repr__(self):
        return (
            f"CatchClause("
            f"{self.exception_type}, "
            f"{self.name}, "
            f"{self.block})"
        )

class TryStatement(StatementNode):
    def __init__(
            self,
            try_block:Block,
            catches:list[CatchClause],
            finally_block:Block|None=None
    ):
        self.try_block = try_block
        self.catches = catches
        self.finally_block = finally_block

    def __repr__(self):
        return (
            f"TryStatement("
            f"{self.try_block}, "
            f"{self.catches}, "
            f"{self.finally_block})"
        )
        