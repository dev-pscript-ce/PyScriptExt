import sys
sys.dont_write_bytecode = True

from.base import ExprNode,StatementNode
from.statements import Block

class ClassDef(StatementNode):
    
    def __init__(self,name:str,body:Block,bases:list[ExprNode],token=None):
        
        super().__init__(token)

        self.name = name
        self.body = body
        self.bases = bases or []


class SuperExpr(ExprNode):
    def __init__(self, token=None):
        super().__init__(token)

class ClassObject:

    def __init__(
        self,
        name,
        scope,
        bases = None
    ):
        self.name = name
        self.scope = scope
        self.bases = bases or []
        
class SuperObject:

    def __init__(

        self,

        instance,

        current_class

    ):

        self.instance = instance

        self.current_class = current_class

class InstanceObject:

    def __init__(self, cls):
        self.cls = cls
        self.fields = {}

    def lookup(self, name):

        if name in self.fields:
            return self.fields[name]

        return self.cls.lookup(name)    
    
class BoundMethod:

    def __init__(self, owner, function):
        self.owner = owner
        self.function = function


