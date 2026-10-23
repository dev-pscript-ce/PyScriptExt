from pathlib import Path

class CV2Module:
    def __init__(self,engine):
        self.engine = engine
    def FIND_IMG(self,img_path,debug=False):
        return self.engine._find_img(img_path,debug=debug)
    def SMART_FIND(self, img_path,debug=False):
        return self.engine._smart_find(img_path,debug=debug)
    def CLICK_IMG(self, img_path):
        return self.engine._click_img(img_path)
    def SMART_CLICK(self, img_path):
        return self.engine._smart_click(img_path)
    def WAIT_IMG(self, img_path):
        return self.engine._wait_img(img_path)
    def CLICK(self,x,y,**kwargs):
        return self.engine._click(x,y,**kwargs)
    def FIND_CLICK(self,target,click=False,**kwargs):
        return self.engine._find_click(
            target,
            click=click,
            **kwargs
        )