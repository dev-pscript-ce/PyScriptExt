import sys
sys.dont_write_bytecode = True

from .base import Node
from pscript.parameter_kind.paramkind import ParameterKind

class Parameter(Node):

    def __init__(
        self,
        name,
        default=None,
        kind=ParameterKind.POSITIONAL,
        token = None,
    ):
        super().__init__(token)
        
        self.name = name

        self.default = default

        self.kind = kind