class OCRModule:
    def __init__(self,engine):
        self.engine = engine
        
    def FIND_TEXT(self, text, **kwargs):
        return self.engine._find_text(
            text,
            **kwargs
        )
    def CLICK_TEXT(self, text):
        return self.engine._click_text(text)
    
    def WAIT_TEXT(self, text):
        return self.engine._wait_text(text)