import sys
sys.dont_write_bytecode = True

class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value 

class BreakSignal(Exception):
    pass

class ContinueSignal(Exception):
    pass