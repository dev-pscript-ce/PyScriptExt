import sys
sys.dont_write_bytecode = True
from pscript.debugs.debug import debug

class RuntimePrinter:
    def call(self,*args):
        debug.log("call",*args)
    
    def _return(self, *args):
        debug.enter("return",*args)

runtime_print = RuntimePrinter()
