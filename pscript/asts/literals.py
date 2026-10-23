import sys
sys.dont_write_bytecode = True

from .base import ExprNode

class Number(ExprNode):
    def __init__(self,value:int|float):
        self.value = value

    def __repr__(self):
        return f"Number({self.value})"

class String(ExprNode):
    def __init__(self,value:str):
        self.value = value
    def __repr__(self):
        return f"String({self.value})"
    
class FString(ExprNode):
    def __init__(self, parts:list[ExprNode]):
        self.parts = parts

class FStringText(ExprNode):
    def __init__(self, value:str):
        self.value = value
        
class Boolean(ExprNode):
    def __init__(self,value:bool):
        self.value = value

    def __repr__(self):
        return f"Boolean({self.value})"
    
class Null(ExprNode):
    def __repr__(self):
        return f"Null()"
    
class ListLiteral(ExprNode):
    def __init__(self,elements:list[ExprNode]):
        self.elements = elements

    def __repr__(self):
        return f"List({self.elements}"
    
class TupleLiteral(ExprNode):
    def __init__(self,elements:list[ExprNode]):
        self.elements = elements

class SetLiteral(ExprNode):
    def __init__(self,elements:list[ExprNode]):
        self.elements=elements
    
class DictLiteral(ExprNode):

    def __init__(self, pairs:list[tuple[ExprNode,ExprNode]]):
        self.pairs = pairs

    def __repr__(self):
        return f"Dict({self.pairs})"