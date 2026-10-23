import sys
sys.dont_write_bytecode = True

class ModuleObject:
    def __init__(self,scope):
        self.scope = scope
    def __getattr__(self, name):
            return self.scope.lookup(name)


    