
class Stack:

    def __init__(self,items=None):
        self.items = [] if items is None else list(items)


    def __repr__(self):
        return f"Stack({self.items})"


    def push(self, x):
        self.items.append(x)

    def pop(self):
        return self.items.pop()