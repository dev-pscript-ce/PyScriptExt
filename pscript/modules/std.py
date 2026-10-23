
class STDModule:
    def __init__(self, engine):
        self.engine = engine

    # console:
    def PRINTL(self,*args):
        return self.engine._printl(*args)

    def INPUTL(self,*args):
        return self.engine._inputl(*args)
    
    def WRITEL(self,*args):
        return self.engine._writel(*args)
    