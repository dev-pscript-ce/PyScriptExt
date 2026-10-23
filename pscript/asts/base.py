import sys
sys.dont_write_bytecode = True

class Node:
    def __init__(self,token=None):
        self.token = token

class ExprNode(Node):
    pass

class StatementNode(Node):
    pass