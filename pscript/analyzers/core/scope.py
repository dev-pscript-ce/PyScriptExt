class Scope:
    def __init__(self, parent=None,name="global",kind="global"):
        self.parent = parent
        self.name = name
        self.kind=kind

        self.symbols = {}

    def define(self, name, symbol):
        self.symbols[name] = symbol

    def contains(self, name):
        return name in self.symbols

    def resolve_local(self, name):

        return self.symbols.get(name)
    
    def resolve(self,name):
        scope = self

        while scope is not None:
            symbol = scope.resolve_local(name)

            if symbol is not None:
                return symbol
            scope = scope.parent
        return None

class ScopeManager:

    def __init__(self):

        self.global_scope = Scope(
            name="global",
            kind="global",
        )

        self.current = (
            self.global_scope
        )

        self.stack = [
            self.global_scope
        ]

    # =================================
    # Enter
    # =================================

    def enter_scope(
        self,
        name,
        kind="block",
    ):

        scope = Scope(
            parent=self.current,
            name=name,
            kind=kind,
        )

        self.stack.append(
            scope
        )

        self.current = scope

        return scope

    # =================================
    # Exit
    # =================================

    def exit_scope(self):

        if len(self.stack) <= 1:

            return self.current

        self.stack.pop()

        self.current = (
            self.stack[-1]
        )

        return self.current

    # =================================
    # Define vào current scope
    # =================================

    def define(
        self,
        name,
        symbol,
    ):

        self.current.define(
            name,
            symbol,
        )

    # =================================
    # Resolve
    # =================================

    def resolve(
        self,
        name,
    ):

        return self.current.resolve(
            name
        )