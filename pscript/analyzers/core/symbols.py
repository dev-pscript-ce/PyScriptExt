import sys 
sys.dont_write_bytecode = True

class Symbols:
    def __init__(self, name, kind, node = None,data=None):
        self.name = name
        self.kind = kind
        self.node = node
        self.data = data



