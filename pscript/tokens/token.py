import sys
sys.dont_write_bytecode = True

from ..debugs.debug import*

class Token:
    def __init__(self, kind, value, line=1, column=1,length=None):

        self.kind = kind
        self.value = value

        self.line = line
        self.column = column
        if length is None:
            
            length = len(str(value)) if value is not None else 1

        self.length = max(
            length,
            1
        )

    def __repr__(self):
        
        return (
            f"{self.kind}"
            f"({self.value})"
        )