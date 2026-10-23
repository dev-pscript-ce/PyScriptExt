import sys 
sys.dont_write_bytecode = True

from pscript.debugs.debug import debug


class Printers:
    def assign(self,*args):
        debug.log("assign", *args)

    def loop(self,*args):
        debug.log("loop",*args)

    def member(self,*args):
        debug.log("member", *args)

    def scope(self,*args):
        debug.log("scope", *args)
    

printers = Printers()