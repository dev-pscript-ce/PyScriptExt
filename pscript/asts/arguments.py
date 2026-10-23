import sys
sys.dont_write_bytecode = True

from.base import ExprNode

class NamedArgument(ExprNode):

    def __init__(self, name, value,token=None):
        super().__init__(token)
        self.name = name
        self.value = value


class StarArgument(ExprNode):

    def __init__(self, value,token=None):
        super().__init__(token)
        self.value = value


class KwStarArgument(ExprNode):

    def __init__(self, value,token=None):
        super().__init__(token)
        self.value = value