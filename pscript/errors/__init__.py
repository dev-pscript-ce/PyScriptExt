import sys
sys.dont_write_bytecode=True

from .pscript_errors import PscriptSyntaxError

__all__ = ["PscriptSyntaxError"]