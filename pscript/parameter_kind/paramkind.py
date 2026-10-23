import sys
sys.dont_write_bytecode = True

from enum import Enum, auto

class ParameterKind(Enum):

    POSITIONAL = auto()

    VAR_POSITIONAL = auto()     # *args

    VAR_KEYWORD = auto()        # **kwargs

    KEYWORD_ONLY = auto()