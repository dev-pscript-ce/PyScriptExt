class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.values = {}

    def define(self, name, value):
        self.values[name] = value
    
    def exists_local(self, name):
        return name in self.values
    
    def get(self, name):

        scope = self.resolve(name)

        if scope is None:
            raise NameError(f"{name} not found")

        return scope.values[name]
    
    def set(self, name,value):
        
        if self.exists_local(name):
            self.assign(name, value)
        else:
            self.define(name, value)
    
    def assign(self, name, value):
        if name in self.values:
            self.values[name] = value
            return
        
        if self.parent:
            self.parent.assign(name, value)
            return
        raise NameError(f"Undefined variable '{name}'")
    
    def assign_or_define(self, name, value):

        scope = self.resolve(name)

        if scope:
            scope.assign(name, value)
        else:
            self.define(name, value)

    def resolve(self, name):

        if name in self.values:
            return self

        if self.parent:
            return self.parent.resolve(name)

        return None
    
    def lookup(self, name):

        if name in self.values:
            return self.values[name]

        if self.parent:
            return self.parent.lookup(name)

        raise NameError(name)