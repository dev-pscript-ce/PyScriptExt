import sys
sys.dont_write_bytecode = True

from .base import Node

class Program(Node):
    def __init__(self, body):
        self.body = body

    def __repr__(self):
        return f"Program({self.body})"