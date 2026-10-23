import sys
sys.dont_write_bytecode = True

from .base import Node,ExprNode

from ..tokens.scope import Scope
from .exceptions import ReturnSignal
from .statements import Block
from .parameters import Parameter


class FunctionCall(ExprNode):

    def __init__(
            self, 
            callee:ExprNode, 
            args:list,
            lparen_token=None,
            rparen_token=None,
            token=None
        ):

        super().__init__(token)

        self.callee = callee

        self.args = args 
        self.lparen_token = lparen_token
        self.rparen_token = rparen_token

class FunctionDef(ExprNode):
    def __init__(self,name:str, params:list[Parameter], body:Node,token=None):
        super().__init__(token)
        self.name = name
        self.params = params
        self.body = body

    def __repr__(self):

        return (
            f"FunctionDef("
            f"{self.name}, "
            f"{self.params}, "
            f"{self.body})"
        )
class FunctionObject:

    def __init__(self, name, params, body, closure):

        self.name = name
        self.params = params
        self.body = body
        self.closure = closure
        self.self_name = None
        self.is_method = False

class LambdaExpr(ExprNode):

    def __init__(self, params:list[Parameter], body:Node):
        self.params = params
        self.body = body

class LambdaFunction:

    def __init__(self, interpreter, node, closure):

        self.interpreter = interpreter
        self.node = node
        self.closure = closure

    def __call__(self, *args):

        interp = self.interpreter

        # Lưu scope hiện tại
        old_scope = interp.current_scope

        # Tạo scope mới, parent là closure
        scope = Scope(self.closure)

        # Bind tham số
        for param, value in zip(self.node.params, args):
            scope.define(param.name, value)

        interp.current_scope = scope

        try:

            # Lambda có body là expression
            if not isinstance(self.node.body, Block):
                return interp.visit(self.node.body)

            # Lambda có body là block
            try:
                interp.visit(self.node.body)
            except ReturnSignal as ret:
                return ret.value

            return None

        finally:
            interp.current_scope = old_scope

class AnonymousFunction:

    def __init__(self, params, body):
        self.params = params
        self.body = body

    def __repr__(self):
        return f"AnonymousFunction({self.params!r})"