import sys,os,re,time,pyperclip
sys.dont_write_bytecode = True

from pathlib import Path
import pyautogui as pag
import unicodedata as unic

def add_root(level: int = 2):
    ROOT_DIR = Path(__file__).resolve().parents[level]

    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))

    return ROOT_DIR

add_root()
# ☝️ 👉 use 👇 current here|👉"python -m dsl.engines.engine"
from ..helpers.color import (
    printl,
    inputl,
    ansi,
    ANSI,
    ANSI_ALIAS
)


from ..engines.engine_base import (
    imgOCRFind, 
    imgCV2Find, 
    imgClick,
    imgReg
    )
        
class Engine():
    def __init__(
            self, 
            delay=0.2, 
            threshold=0.8, 
            runtime=None,
            multi_scale=True
        ):
        self.delay = delay
        self.threshold = threshold
        self.multi_scale = multi_scale
        self.default_interval = 0
        self.ctx = {}
        self.name="name"
        self.runtime = runtime

    def text_to_img_name(self, text):

        text = self.remove_accents(text)

        text = re.sub(r"\d+", "", text)
        text = re.sub(r"[^\w]+", "_", text)
        text = re.sub(r"_+", "_", text)

        text = text.strip("_")

        return f"{text}.png"
    
    # hàm bỏ dấu TV:
    def remove_accents(self,text):

        text = (
            unic
            .normalize("NFD", text)
        )

        text = "".join(
            c for c in text
            if unic.category(c) != "Mn"
        )

        text = (
            text.replace("đ", "d")
                .replace("Đ", "D")
                .replace(" ", "_")
                .lower()
        )
    
        return text
# ========== basic =========
    def _write(self, text, **kwargs):

        kwargs.setdefault(
            "interval",
            self.default_interval
        )

        if any(ord(c) > 127 for c in text):
            pyperclip.copy(text)
            pag.hotkey("ctrl","v")
            return
        pag.write(text,**kwargs)
        

    def _type_write(self, text, **kwargs):

        kwargs.setdefault(
            "interval",
            self.default_interval
        )

        if any(ord(c) > 127 for c in text):
            pyperclip.copy(text)
            pag.hotkey("ctrl","v")
            return

        pag.typewrite(text, **kwargs)

    def _press(self, key, **kwargs):
        pag.press(key, **kwargs)

    def _hotkey(self, *keys, **kwargs):

        if len(keys) == 1:

            keys = tuple(
                keys[0].split()
            )

        pag.hotkey(*keys, **kwargs)

    def _set_interval(self, value):
        self.default_interval = value

    def _key_down(self,key):
        pag.keyDown(key)

    def _key_up(self,key):
        pag.keyUp(key)

    def _click(self, x, y, **kwargs):
        pag.click(x, y, **kwargs)

    def _double_click(self, x, y, **kwargs):
        pag.doubleClick(x, y, **kwargs)

    def _sleep(self, seconds):
        time.sleep(seconds)

    def _move_rel(
        self,
        target1,
        target2,
        click_img=False,
        **kwargs
    ):

        # ==========================
        # mode: image -> image
        # ==========================

        if isinstance(target1, str):

            pos1 = imgCV2Find.smart_find(
                target1,
                threshold=self.threshold,
                return_type="tuple"
            )
            if not pos1:
                raise Exception(
                    f"Image not found: {target1}"
                )

            pos2 = imgCV2Find.smart_find(
                target2,
                threshold=self.threshold,
                return_type="tuple"
            )

            if not pos2:
                raise Exception(
                    f"Image not found: {target2}"
                )

            dx = pos2[0] - pos1[0]
            dy = pos2[1] - pos1[1]

            pag.moveRel(dx, dy, **kwargs)

            if click_img:
                imgClick.clicks(pos2)

            return (dx, dy)

        # ==========================
        # mode: x,y
        # ==========================

        x = int(target1)
        y = int(target2)

        pag.moveRel(x, y, **kwargs)

        if click_img:
            pag.moveTo(x,y)
            pag.click()

        return (x, y)

    
    def _move_to_img(self, img_path,**kwargs):
        pos = imgCV2Find.smart_find(
            img_path,
            threshold=self.threshold
        )
        if not pos:
            raise Exception(
                f"Image not found:{img_path}"
            )
        pag.moveRel(
            pos[0],
            pos[1],
            **kwargs
        )
        return pos

# ------------------------------------------ 

    def _create_file(self, name="auto_name", ext="ps"):
        if self.runtime and self.runtime.file_stack:
            base = self.runtime.file_stack[-1].parent
        else:
            base = Path.cwd()

        path = base / f"{name}.{ext}"

        if path.exists():
            self._printl(f"⚠️  File '{path.name}' đã tồn tại", "rY1")
            return path

        path.touch()
        self._printl(f"Đã tạo '{path.name}' ✅", "G")

        return path

# -----------------------------------------------------------
# ============= OCR ==============
    def _find_text(
        self,
        text,
        region=None,
        size=None,
        debug=False,
        save_temp=False,
        click=False,
        **kwargs
    ):
        
        if region is None:

            if size is None:
                size = (60,20)

            region = imgReg.region_from_pos(
                size=size
            )


        return imgOCRFind.find_text(
            text=text,
            region=region,
            debug=debug,
            save_temp=save_temp,
            click=click,
            **kwargs
        )

    
    def _click_text(self, text):

        assets_dir = self.runtime.get_assets_dir(create=True)

        img_name = self.text_to_img_name(text)

        base = assets_dir or imgCV2Find.assets_dir

        img_path = os.path.join(
            base,
            img_name
        )

        # ==========================
        # Template chưa tồn tại
        # ==========================

        if not os.path.exists(img_path):

            print(
                f"[AUTO CREATE] {img_name}"
            )

            ocr_pos = imgOCRFind.find_text(
                text=text,
                region=imgReg.region_from_pos(
                    size=(60,20)
                ),
                debug=True,
                save_temp=True,
            )

            if not ocr_pos:
                raise Exception(
                    f"Text not found: {text}"
                )

        # ==========================
        # CV2
        # ==========================

        pos = imgCV2Find.smart_find_cv2_text(
            img_name,
            debug=True
        )

        if not pos:
            raise Exception(
                f"Text not found: {text}"
            )

        imgClick.clicks(pos)

        return pos
    
    def _wait_text(
        self,
        text,
        timeout=5,
        interval=0.5,
        region=None,
        size=None,
        **kwargs
    ):

        if region is None and size:
            region = imgReg.region_from_pos(
                size=size
            )

        start = time.time()

        while time.time() - start < timeout:

            result = imgOCRFind.find_text(
                text=text,
                region=region,
                **kwargs
            )

            if result:
                print(
                    f"[FOUND] {text}"
                )
                return result

            time.sleep(interval)

        raise TimeoutError(
            f"Text not found: {text}"
        )

    # ============= OCR ==============
    def _find_img(
            self,
            img_path,
            region=None,
            debug=False,
            **kwargs
    ):
        return imgCV2Find.find(
            img_path,
            region=region,
            # threshold=kwargs.pop("threshold", self.threshold),
            threshold = self.threshold,
            multi_scale=kwargs.pop("multi_scale", self.multi_scale),
            debug=debug,
            **kwargs
        )
    
    def _smart_find(self, img_path,debug=False, **kwargs):
        return imgCV2Find.smart_find(
            img_path,
            # threshold=kwargs.pop("threshold", self.threshold),
            debug=debug,
            **kwargs
        )
    def _click_img(self, img_path, region=None):
        return imgClick.clicks(
            img_path,
            region=region,
        )
    def _find_click(self, img_path, region=None,click=False):

        path = Path(img_path)

        # Nếu không có extension 
        if not path.suffix:
            printl.R(
                f'[CV2] Img extension not specified: "{path.name}" -> using ".png"'
            )
            path = path.with_suffix(".png")
            img_path = str(path)

        # Kiểm tra file
        try:
            return imgClick.find_click(
                img_path,
                region=region,
                click=click
            )

        except Exception as e:
            printl.G(f'[CV2] {e}')
            return False
    
    def _smart_click(self, img_path):
        pos = imgCV2Find.smart_find(
            img_path,
            threshold=self.threshold
        )
        if not pos:
            raise Exception(f"Image not found: {img_path}")
        imgClick.clicks(pos)
        return pos

    def _wait_img(
            self, 
            image, 
            timeout=5, 
            interval=0.5, 
            region=None
        ):
        
        start = time.time()

        while time.time() - start < timeout:

            pos = imgCV2Find.find(
                image,
                region=region,
                threshold=self.threshold,
                multi_scale=self.multi_scale
            )

            if pos:
                return pos

            time.sleep(interval)

        raise TimeoutError(f"Image not found: {image}")
        

    def _printl(self, *args):

        if not args:
            return printl()

        # ------------------------------------------
        # Tuple mode
        # ------------------------------------------

        if all(
            isinstance(arg, tuple)
            for arg in args
        ):

            normalized = []

            for item in args:

                if len(item) != 2:
                    raise TypeError(
                        "Printl: tuple phải có dạng "
                        "(text, style)"
                    )

                text, style = item

                if isinstance(style, str):
                    style = self._resolve_printl_style(
                        style
                    )

                normalized.append(
                    (text, style)
                )

            return printl(*normalized)

        # ------------------------------------------
        # Last argument = Show method name
        # ------------------------------------------

        if (
            len(args) >= 2
            and isinstance(args[-1], str)
        ):

            name = args[-1]

            text = " ".join(
                map(str, args[:-1])
            )

            # ======================================
            # Semantic Show methods
            # ======================================

            semantic = {

                "error": printl.error,
                "warn": printl.warn,
                "info": printl.info,
                "logt": printl.logt,
                "log": printl.log,

            }

            func = semantic.get(
                name
            )

            if func is not None:

                return func(text)

            # ======================================
            # ANSI Show methods
            # ======================================

            if (
                name in ANSI
                or name in ANSI_ALIAS
            ):

                style = (
                    self._resolve_printl_style(
                        name
                    )
                )

                return printl(
                    (text, style)
                )

        # ------------------------------------------
        # Plain
        # ------------------------------------------

        return printl(
            " ".join(
                map(str, args)
            )
        )
    def _inputl(self, *args):

        if not args:
            return inputl()

        # ------------------------------------------
        # Tuple mode
        # ------------------------------------------

        if all(
            isinstance(arg, tuple)
            for arg in args
        ):

            normalized = []

            for item in args:

                if len(item) != 2:
                    raise TypeError(
                        "Inputl: tuple phải có dạng "
                        "(text, style)"
                    )

                text, style = item

                if isinstance(style, str):
                    style = self._resolve_inputl_style(
                        style
                    )

                normalized.append(
                    (text, style)
                )

            return inputl(*normalized)

        # ------------------------------------------
        # Last argument = show method name
        # ------------------------------------------

        if (
            len(args) >= 2
            and isinstance(args[-1], str)
        ):

            name = args[-1]

            text = " ".join(
                map(str, args[:-1])
            )

            # ======================================
            # ANSI Show methods
            # ======================================

            if (
                name in ANSI
                or name in ANSI_ALIAS
            ):

                style = (
                    self._resolve_inputl_style(
                        name
                    )
                )

                return inputl(
                    (text, style)
                )

        # ------------------------------------------
        # Plain
        # ------------------------------------------

        return inputl(
            " ".join(
                map(str, args)
            )
        )

    

    def _resolve_printl_style(
        self,
        name,
    ):

        if not isinstance(
            name,
            str,
        ):
            return name

        name = ANSI_ALIAS.get(
            name,
            name,
        )

        # =================================
        # ANSI style
        # =================================

        func = getattr(
            ansi,
            name,
            None,
        )

        if callable(func):
            return func

        # =================================
        # Printl semantic style
        # =================================

        PRINTL_STYLES = {

            "warn": printl.warn,
            "error": printl.error,
            "logt": printl.logt,

        }

        func = PRINTL_STYLES.get(
            name
        )

        if callable(func):
            return func

        raise ValueError(
            f"Printl API không hỗ trợ style: {name!r}"
        )
    def _resolve_inputl_style(
        self,
        name,
    ):

        if not isinstance(
            name,
            str,
        ):
            return name

        name = ANSI_ALIAS.get(
            name,
            name,
        )

        # =================================
        # ANSI style
        # =================================

        func = getattr(
            ansi,
            name,
            None,
        )

        if callable(func):
            return func

        raise ValueError(
            f"Inputl API không hỗ trợ style: {name!r}"
        )

    def _writel(self, text, *args):

        STRING_MAP = {
            "R":"R",
            "G": "G",
            "Y": "Y",
            "B": "B",
            "M": "M",
            "C": "C",
            "W": "W",
            "A": "A",

            "i": "i",
            "u": "u",
            "b": "b",

            "rR": ansi.rgb(255, 0, 0),
            "rG": ansi.rgb(0, 255, 0),
            
            "hR": ansi.hex("#f00"),
            "discord": ansi.hex("#5865f2")
        }
        color = STRING_MAP["A"]

        if args and isinstance(args[-1], str):
            color = args[-1]
            args = args[:-1]

        if color in STRING_MAP:
            return getattr(printl, STRING_MAP[color])(text, *args)

        return printl(text, *args)


    def _range(self,*args):
        return range(*args)
    def _push(self,lst,value):
        lst.append(value)
    def _pop(self,lst):
        return lst.pop()

    def _split(
            self,
            separator="",
            item=None,
            limit=None,
            str_single_value=False,
            index_filter=None,
    ):
        if item is None:
            return []
        if isinstance(item, str):
            if separator == "":
                result = list(item)
            else:
                result = item.split(separator)
            if str_single_value:
                if separator == "":
                    result = [",".join(str(x) for x in item)]
                return result
            if limit is not None:
                result = result[:max(0,limit)]
            if index_filter is not None:
                try:
                    return result[index_filter]
                except IndexError:
                    return (self._error("Index out of range",ps_err=False))
                
    def _join(self, separator="", item=None):
        if item is None:
            return ""

        try:
            return str(separator).join(str(x) for x in item)
        except TypeError:
            return str(item)
    
    def _error(self,err_text=None, warn_text=None, throw_err=True):
        if warn_text is None:
            warn_text = []
            
        if throw_err :
            printl.error("❌", err_text)
            return False


        # normalize warn_text
        if isinstance(warn_text, str) :
            warn_text = list(warn_text)

        if len(warn_text) > 0 and warn_text[0] :
            printl(("⚠️  " + str(warn_text[0]),"Y"))
        if len(warn_text) > 1 and warn_text[1] :
            printl(("⚠️  " + str(warn_text[1]),"rY1"))

        return False
    
    def _ask_option(self,question, options, is_num=True):
        while True:

            printl.info("===", question, "===")

            for i, option in enumerate(options):

                if is_num:
                    key = str(i + 1)
                else:
                    key = chr(97 + i)

                printl((key,"M"),("▸","B"), (option,"B"))

            if is_num:
                prompt = f"Chọn 1-{len(options)} :"
            else:
                prompt = f"Chọn a-{chr(96 + len(options))} :"

            choice = inputl((prompt, "Y"))

            if is_num:
                if choice.isdigit():
                    num = int(choice)

                    if 1 <= num <= len(options):
                        return num

            else:
                if len(choice) == 1:
                    index = ord(choice.lower()) - 96

                    if 1 <= index <= len(options):
                        return index

            inputl((
                "❌ Invalid selection; please select again!",
                "rR",
            ))



