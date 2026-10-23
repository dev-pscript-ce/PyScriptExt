import cv2,mss,json,sys,time,os,re,traceback

sys.dont_write_bytecode = True

from pathlib import Path

def add_root(level: int = 2):
    ROOT_DIR = Path(__file__).resolve().parents[level]

    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))

    return ROOT_DIR
add_root()

import numpy as np
import pyautogui as pag
import pytesseract as pyt
import unicodedata as unic

from PIL import Image
from random import randrange as rand
from threading import Lock
# Import API
from pscript.helpers.color import printl,c

pyt.pytesseract.tesseract_cmd = \
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"

counter = 0
last_ts = 0
lock = Lock()

# ====================================================== # 

DEFAULT_ASSETS = (
    Path(__file__)
    .resolve()
    .parent
    / "assets"
)

class AutoBase:

    _runtime = None

    def get_assets_dir(self, create=False) -> Path:

        if self.runtime is not None:
            return self.runtime.get_assets_dir(
                create=create
            )

        path = DEFAULT_ASSETS

        if create:
            path.mkdir(
                parents=True,
                exist_ok=True
            )

        return path

    # def get_assets_dir(self, create=False) -> Path:

    #     if self.runtime is None:
    #         raise RuntimeError(
    #             "Runtime chưa được bind"
    #         )

    #     return self.runtime.get_assets_dir(
    #         create=create
    #     )

    def get_assets_path(self, path: str|Path,create=False) -> Path:

        p = Path(path)

        if p.is_absolute():
            return p
        
        return self.get_assets_dir(create=create)/p

    @staticmethod
    def bind_runtime(runtime):
        AutoBase._runtime = runtime

    @property
    def runtime(self):
        return AutoBase._runtime
    

class Normalize(AutoBase):
    def __init__(self, threshold=0.6, multi_scale=True):
        self.threshold = threshold
        self.multi_scale = multi_scale

    def normalize_template(self, target):

        if not target:
            return None

        # -------------------------
        # string
        # -------------------------

        if isinstance(target, str):

            if target.lower().endswith((
                ".png",
                ".jpg",
                ".jpeg",
                ".bmp",
                ".webp"
            )):
                return target

        # -------------------------
        # dict
        # -------------------------

        elif isinstance(target, dict):

            # {"path":"btn.png"}
            if "path" in target:
                return target["path"]

            # {"template":"btn.png"}
            if "template" in target:
                return target["template"]

            # {"img":"btn.png"}
            if "img" in target:
                return target["img"]

        # -------------------------
        # tuple/list
        # -------------------------

        elif isinstance(target, (tuple, list)):

            # ("btn.png",x,y)
            if len(target) >= 1 and isinstance(target[0], str):
                return target[0]

        return None
    
    def normalize_region(self, region):

        if not region:
            return None

        # -------------------------
        # dict
        # -------------------------

        if isinstance(region, dict):

            # {"region":(...)}
            if "region" in region:
                return region["region"]

            # {"rect":(...)}
            if "rect" in region:
                return region["rect"]

            # {"x":0,"y":0,"w":100,"h":100}
            if all(k in region for k in ("x", "y", "w", "h")):

                return (
                    region["x"],
                    region["y"],
                    region["w"],
                    region["h"]
                )

        # -------------------------
        # tuple/list
        # -------------------------

        elif isinstance(region, (tuple, list)):

            # (x,y,w,h)
            if (
                len(region) == 4
                and all(isinstance(v, (int, float)) for v in region)
            ):
                return tuple(region)

            # [(x,y,w,h),(...)]
            elif (
                len(region) > 0
                and isinstance(region[0], (tuple, list))
            ):

                fixed = []

                for r in region:

                    nr = self.normalize_region(r)

                    if nr:
                        fixed.append(nr)

                return fixed

        return None
    
    def normalize_pos(self, pos):
        if not pos:
            return None
        
        # dict:
        if isinstance(pos, dict):
            # center:
            if "x" in pos and "y" in pos:
                return (pos["x"],pos["y"])
            # center tuple:
            if "center" in pos:
                return pos["center"]
            # rect:
            if "rect" in pos:
                x, y, w, h = pos["rect"]
                return(x + w // 2, y + h // 2)
        # tuple/list:
        elif isinstance (pos, (tuple,list)):
            # (x,y):
            if len(pos)==2:
                return (pos[0],pos[1])
            elif len(pos) == 4 and all(isinstance(v, (int,float))for v in pos):
                x,y,w,h = pos
                return (x + w // 2, y + h // 2)
            # (path, x, y):
            elif len(pos) >= 3 and isinstance(pos[0], str):
                return (pos[1], pos[2])
            # (path,x,y,w,h):
            elif len(pos) >= 5 and isinstance(pos[0],str):
                _, x, y, w, h = pos[:5]
                return (x + w // 2, y + h // 2)
            
        elif isinstance(pos, str):

            # img path
            if pos.lower().endswith((
                ".png",
                ".jpg",
                ".jpeg",
                ".bmp",
                ".webp"
            )):
                return None
            # debug string
            m = re.search(r"\((\d+)\s*,\s*(\d+)\)", pos)

            if m:
                return (int(m.group(1)), int(m.group(2)))
        return None
    
    def normalize_input(self, data):

        if not data:
            return None

        result = {
            "path": None,
            "pos": None,
            "region": None,
        }

        # -------------------------
        # dict
        # -------------------------

        if isinstance(data, dict):

            result["path"] = self.normalize_template(data)

            result["pos"] = self.normalize_pos(data)

            result["region"] = self.normalize_region(data)

            return result

        # -------------------------
        # string
        # -------------------------

        elif isinstance(data, str):

            result["path"] = self.normalize_template(data)

            result["pos"] = self.normalize_pos(data)

            return result

        # -------------------------
        # tuple/list
        # -------------------------

        elif isinstance(data, (tuple, list)):

            # region
            nr = self.normalize_region(data)

            if nr:
                result["region"] = nr

            # pos
            np = self.normalize_pos(data)

            if np:
                result["pos"] = np

            # template
            nt = self.normalize_template(data)

            if nt:
                result["path"] = nt

            return result

        return result

# ====================================================== #
unify = Normalize()

# ====================================================== #
class OCRFinder(AutoBase):
    def __init__(self):
        # các icon/symbol OCR hay đọc sai
        self.icon_chars = "►▶▸▹⏵⯈<>|=+~˅∨⌄▼▾^˄⌃∧▲⏶"

        # các kết quả OCR rác thường gặp
        self.bad_ocr = {
            "pv", "vv","dv" ,"cv",
            "pb"
            "cy","py"
            ">", "<", "^","[>"
            "av", "rv","dv","Dv"
        }

    # =======================
    def safe_filename(self, text, replace="_"):
        if not text:
            return "file"

        # unicode normalize
        text = unic.normalize("NFC", str(text)).strip().lower()

        # debug thật sự OCR đọc gì
        # print("[RAW OCR]:", repr(text))
        print("[RAW OCR]:", text)

        # ===== remove icon chars =====
        text = re.sub(
            f"[{re.escape(self.icon_chars)}]",
            "",
            text
        )

        text = text.strip()

        # ===== OCR rác =====
        if text in self.bad_ocr:
            return "icon"

        # quá ngắn => khả năng icon
        if len(text) <= 2:
            return "icon"

        # ===== bỏ số =====
        text = re.sub(r"\d+", "", text)

        # ===== replace ký tự đặc biệt =====
        text = re.sub(
            r"[\\/*?!@#$%^&+'`\-:\"<>|,.{}()\[\]\s;]+",
            replace,
            text
        )

        # ===== gộp ___ =====
        text = re.sub(
            rf"{re.escape(replace)}+",
            replace,
            text
        )

        # ===== strip =====
        text = text.strip(replace)

        # ===== empty =====
        # chỉ lấy tối đa N từ
        words = text.split("_")

        # bỏ từ quá ngắn
        words = [w for w in words if len(w) > 1]

        # lấy tối đa 2 từ
        text = "_".join(words[:2])

        if not text:
            return "icon"

        return text

    # =======================
    def find_text(
            self,
            text,
            region=None,
            debug=False,
            save_temp=False,
            click=False
        ):
            img, monitor = scrCapture.capture(region, gray=False)

            gray = cv2.cvtColor(
                img,
                cv2.COLOR_BGR2GRAY
            )

            # =========================
            # ZOOM
            # =========================

            scale = 2

            gray = cv2.resize(
                gray,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_CUBIC
            )

            # =========================
            # SHARPEN
            # =========================

            kernel = np.array([
                [0, -1, 0],
                [-1, 5, -1],
                [0, -1, 0]
            ])

            gray = cv2.filter2D(
                gray,
                -1,
                kernel
            )

            # =========================
            # THRESHOLD
            # =========================

            _, gray = cv2.threshold(
                gray,
                180,
                255,
                cv2.THRESH_BINARY
            )

            cv2.imwrite(
                "debug_ocr.png",
                gray
            )

            # =========================
            # OCR
            # =========================

            pil_img = Image.fromarray(gray)

            data = pyt.image_to_data(
                pil_img,
                output_type=pyt.Output.DICT,
                config="--oem 3 --psm 7"
            )

            words = []

            for i, word in enumerate(data["text"]):

                word = word.strip()

                if not word:
                    continue

                try:
                    conf = int(float(data["conf"][i]))
                except Exception:
                    conf = 0

                if conf < 30:
                    continue

                words.append(word)

                if debug:
                    print(
                        f"[OCR] {word} | conf={conf}"
                    )

            full_text = " ".join(words).lower()

            if debug:
                printl(
                    ("[OCR TEXT]:", "G"),
                    (full_text, "C")
                )

            # =========================
            # SAVE OCR IMAGE
            # =========================

            _text_ = self.safe_filename(full_text)

            if save_temp:

                assets_dir = self.get_assets_dir(
                    create=True
                )

                print(
                    "OCR ASSETS:",
                    assets_dir
                )

                imgScrSave.screenshot_saveto_assets_help(
                    _text_
                )

            # =========================
            # SEARCH TARGET
            # =========================

            target = text.lower().strip()

            words_lower = [
                w.strip().lower()
                for w in data["text"]
                if w.strip()
            ]

            for start in range(
                len(words_lower)
            ):

                current = ""

                for end in range(
                    start,
                    len(words_lower)
                ):

                    current = (
                        current
                        + " "
                        + words_lower[end]
                    ).strip()

                    if current != target:
                        continue

                    # =========================
                    # MATCHED WORDS
                    # =========================

                    idxs = list(
                        range(
                            start,
                            end + 1
                        )
                    )

                    lefts = [
                        data["left"][i]
                        for i in idxs
                    ]

                    tops = [
                        data["top"][i]
                        for i in idxs
                    ]

                    rights = [
                        data["left"][i]
                        + data["width"][i]
                        for i in idxs
                    ]

                    bottoms = [
                        data["top"][i]
                        + data["height"][i]
                        for i in idxs
                    ]

                    # =========================
                    # BOUNDING BOX
                    # =========================

                    x1 = min(lefts)
                    y1 = min(tops)

                    x2 = max(rights)
                    y2 = max(bottoms)

                    # =========================
                    # CENTER
                    # =========================
                    #
                    # OCR image đã scale x2
                    # => chuyển về tọa độ ảnh gốc
                    #

                    x = (
                        (x1 + x2) // 2
                    ) // scale

                    y = (
                        (y1 + y2) // 2
                    ) // scale

                    # =========================
                    # SCREEN COORDINATE
                    # =========================

                    screen_x = (
                        monitor["left"]
                        + x
                    )

                    screen_y = (
                        monitor["top"]
                        + y
                    )

                    if debug:

                        print(
                            f"[OCR MATCH] "
                            f"{target!r}"
                        )

                        print(
                            f"[BOX] "
                            f"({x1}, {y1}) "
                            f"-> "
                            f"({x2}, {y2})"
                        )

                        print(
                            f"[SCREEN] "
                            f"({screen_x}, "
                            f"{screen_y})"
                        )

                    # =========================
                    # CLICK
                    # =========================

                    if click:

                        pag.click(
                            screen_x,
                            screen_y
                        )

                        if debug:
                            print(
                                f"[OCR CLICK] "
                                f"({screen_x}, "
                                f"{screen_y})"
                            )

                    return (
                        screen_x,
                        screen_y
                    )

            return None

imgOCRFind= OCRFinder()
# ====================================================== # 
#  
class Clicker(AutoBase):
    def __init__(self, threshold=0.6, multi_scale=True):

        super().__init__()

        self.threshold = threshold
        self.multi_scale = multi_scale
        

    def clicks(self, target, region=None):

        data = unify.normalize_input(target)

        # image path
        if data["path"]:

            found = imgCV2Find.find(
                data["path"],
                region=region,
                threshold=self.threshold,
                multi_scale=self.multi_scale
            )

            point = unify.normalize_pos(found)

        else:
            point = data["pos"]

        if not point:
            return None

        x, y = point

        pag.click(x, y)

        return point


    def find_click(self, target, region=None,**kw):
        
        click = kw.pop("click",False)
        debug = kw.pop("debug",False)

        data = unify.normalize_input(target)
        
        temp_path = data["path"]
        if not temp_path:
            return None
        
        region = (
            unify.normalize_region(region=region)
            or data["region"]
        )
        
        # already region/pos
        if isinstance(target, (tuple, list, dict)):
            return self.clicks(target)

        # image path
        pos = imgCV2Find.find(
            target,
            region=region,
            threshold=self.threshold,
            multi_scale=self.multi_scale,
            debug=debug,
            **kw
        )
        if debug:
            return pos
        
        if click:
            self.clicks(pos)
            return pos
        else:
            return pos
    
    def smart_find_single(self, temp_path):
        region = imgCV2Find.smart_find(
            temp_path,
            threshold=self.threshold
        )
        if not region:
            raise Exception(f"❌ Không tìm thấy: {temp_path}")
        self.clicks(region)
        return region
    
    def smart_find_regions(self, img_path, regions,delay=0.3):
        for r in regions:
            if self.find_click(img_path,region=r,click=True):
                printl.G("Hit Region", r)
                return True
            time.sleep(delay)
        printl.B("[fallback fullscreen]")
        return self.find_click(img_path,region=r,click=True)

    def smart_find_mouse_priority(
        self,
        img_path,
        regions,
        delay=0.3
    ):

        # single region -> list
        if (
            isinstance(regions, (tuple, list))
            and len(regions) == 4
            and all(isinstance(v, (int, float)) for v in regions)
        ):
            regions = [regions]

        mx, my = imgPos.from_pos()

        def dist(r):

            x, y, w, h = r

            cx = x + w // 2
            cy = y + h // 2

            return abs(cx - mx) + abs(cy - my)

        regions = sorted(regions, key=dist)

        for r in regions:

            if self.clicks(img_path, region=r):

                printl.G("[Hit]", r)

                return True

            time.sleep(delay)

        return False
                
    def smart_find_best(self, img_path, regions):

        # single region -> list
        if (
            isinstance(regions, (tuple, list))
            and len(regions) == 4
            and all(isinstance(v, (int, float)) for v in regions)
        ):
            regions = [regions]

        best = None

        for r in regions:
            reg = imgCV2Find.find(
                img_path,
                region=r,
                threshold=self.threshold,
                multi_scale=self.multi_scale
            )

            if not reg:
                continue

            conf = reg["confidence"]

            if not best or conf > best["confidence"]:
                best = reg

        if not best:
            return None

        x, y = best["pos"]

        self.clicks((x,y),region=r)

        return best
                 
    def smart_find_ultra(self, img_path, text=None, region=None):

        pos = imgCV2Find.smart_find_cv2_ocr(
            img_path, 
            text=text,
            region=region
        )

        if not pos:
            raise Exception(f"❌ Không tìm thấy: {img_path}")
        self.clicks(pos)
        return pos

    def both_click(self,img_path):
        for r in imgReg.get_regions(mode="half"):
            self.clicks(img_path, region=r)

# # ====================================================== #                      

imgClick = Clicker()

class ScreenCapture(AutoBase):
    def __init__(self, monitor=1,screen_padding=0):
        self.sct = mss.MSS()
        self.monitor = self.sct.monitors[monitor]

        self.screen_w,self.screen_h = pag.size()
        self.pad = screen_padding

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_dir = os.path.join(self.base_dir, "assets")

        # 🔥 cache file
        self.cache_file = os.path.join(self.base_dir, "pos_cache.json")
        self.cache = self.load_cache()

    # ===== CACHE =====
    def load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as f:
                return json.load(f)
        return {}

    def save_cache(self,cache):
        with open(self.cache_file, "w") as f:
            json.dump(cache, f,indent=4)

    def get_cached_region(self, name, w=400, h=200):
        pos = self.cache.get(name)
        if not pos:
            return None
        point = unify.normalize_pos(pos)
        if not point:
            return None
        x, y = point
        return (x - w//2, y - h//2, w, h)

    # ===== CORE =====
    def capture(self, region=None, gray=False):
        monitor = self.monitor if not region else {
            "top": region[1],
            "left": region[0],
            "width": region[2],
            "height": region[3]
        }

        img = np.array(self.sct.grab(monitor))
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        if gray:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        return img, monitor

    def load_template(self, temp_path):

        path = self.get_assets_path(temp_path,create=True)

        if not os.path.exists(path):
            raise Exception(f"❌ Không tìm thấy file: {path}")

        template = cv2.imread(path)

        if template is None:
            raise Exception(f"❌ Không đọc được ảnh: {path}")

        return template

# ====================================================== #
scrCapture = ScreenCapture()

# ====================================================== #
class Positions(AutoBase):
    def __init__(self):
        pass
    
    def from_pos(self,debug=False):
        p = pag.position()
        x, y = p.x, p.y
        if debug:
            printl.C(f"Point{x,y}")
        return x,y

    def from_img(self,img,debug=False):
        reg = imgCV2Find.find(img, threshold=0.9, multi_scale=True)
        if debug:
            printl.C(f"Img[{img}]: Point{reg}")
        return reg
    
# ====================================================== #
imgPos = Positions()

# ====================================================== #
class Regions(AutoBase):
    def __init__(self,screen_pad=0):
        self.screen_w, self.screen_h = pag.size()
        self.pad = screen_pad

    def region_from_pos(self, x=None, y=None, size=(400,200),debug=False):
        if x is None or y is None:
            p = pag.position()
            x, y = p.x, p.y
        w, h = size

        region = (x - w//2, y - h//2, w, h)
        region = self.clamp(region)
        
        if debug:
            printl.G(f"[region_from_pos]: Region{region}")
        return region
    
    def clamp(self, region):
        x, y, w, h = region

        x = max(self.pad, x)
        y = max(self.pad, y)

        w = min(w, self.screen_w - x)
        h = min(h, self.screen_h - y)

        return (x, y, w, h)

    # 🔍 Multi-region scan
    def multi_regions(self, points, size=(400, 200)):
        if isinstance(points, tuple) and len(points) == 2:
            points = [points]

        return [self.region_from_pos(x, y, size) for (x, y) in points]

    def get_regions(self, rx=0,ry=0.95, mode=None, size=(400,200),debug=False):
        def make_region(ratio_x):
            x = int(self.screen_w * ratio_x)
            y = int(self.screen_h * ry)
            
            return self.region_from_pos(x, y, size)
    
        def half_screen (mode):
            r = (self.screen_w // 2, 0, self.screen_w // 2, self.screen_h)
            l = (0, 0, self.screen_w // 2, self.screen_h)
            if mode == "half_r":
                return r
            elif mode == "half_l":
                return l
            elif mode == "full_s":
                return l,r
                
        # ===== ratio =====
        r = make_region(0.8)
        l = make_region(0.2)
        m = make_region(0.5)
        reg = make_region(rx)

        # ===== half_screen =====
        h_r = half_screen(mode="half_r")
        h_l = half_screen(mode="half_l")
        f_s = half_screen(mode="full_s")

        if debug :
            if mode is None:
                if 1 > rx > 0.5 :
                    printl.C(f"[right_ratio]:(rx = {rx:.1f}, ry = {ry:.2f}) -> region{reg}" )

                elif 0 < rx < 0.5:
                    printl.M(f"[left_ratio]:(rx = {rx:.1f}, ry = {ry:.2f}) -> region{reg}" )

                elif rx == 0.5:
                    printl.Y(f"[midle_ratio]:(rx = {rx:.1f}, ry = {ry:.2f}) -> region{reg}" )

                elif rx == 1 :
                    printl.Y(f"[right_ratio]:(rx = {rx*4/5:.1f}, ry = {ry:.2f}) -> region{r}" )
                    printl.M(f"[left_ratio]:(rx = {rx/5:.1f}, ry = {ry:.2f}) -> region{l}" )

                elif rx == -1:
                    printl.G(f"half_screen:{f_s}")
                else :
                    printl.B(f"[right_ratio]:(rx = {rx+0.8:.1f}, ry = {ry:.2f}) -> region{r}" )
                    printl.G(f"[left_ratio]:(rx = {rx+0.2:.1f}, ry = {ry:.2f}) -> region{l}" )

            elif mode == "ratio_r" :
                printl.G(f"[right_ratio]: region{r}" )
            elif 1 > rx > 0.5:
                printl.G(f"[right_ratio]:(rx = {rx:.1f}, ry = {ry:.2f}) -> region{reg}" )

            elif mode == "ratio_l":
                printl.C(f"[left_ratio]: region{l}" )
            elif 0 < rx < 0.5:
                printl.C(f"[left_ratio]:(rx = {rx:.2f}, ry = {ry:.2f}) -> region{reg}" )

            elif mode == "ratio_m":
                printl.C(f"[midle_ratio]:region{m}" )

            elif mode == "half_r":
                printl.G(f"[right_half]:region{h_r}" )

            elif mode == "half_l":
                printl.G(f"[left_half]:region{h_l}" )

            elif mode == "half":
                printl.G(f"[full_screen]:region{f_s}" )

            elif mode == "ratio":
                printl.C(f"[right_ratio]: {r}" )
                printl.A(f"[left_ratio]: {l}" )

        elif mode == "ratio_r" :
            return r
        elif 1 > rx > 0.5 :
            return reg

        elif mode == "ratio_l" :
            return l
        
        elif 0 < rx < 0.5 :
            return reg
        
        elif mode == "ratio_m" or rx == 0.5:
            return m
            
        elif mode == "ratio" or rx == 1:
            return l, r 
        
        elif mode == "half_r":
            return h_r  
        
        elif mode == "half_l":
            return h_l  
        
        elif mode == "half" or rx == -1:
            return h_r, h_l  
        return r,l
    
    def grid(self, rows, cols, r, c):
        cell_w = self.screen_w // cols
        cell_h = self.screen_h // rows
        x = c * cell_w
        y = r * cell_h
        return (x, y, cell_w, cell_h)
    
# ====================================================== #        
imgReg = Regions()

# ====================================================== #


# ====================================================== #
class ScreenShot(AutoBase):
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_dir = os.path.join(self.base_dir, "assets")

    def screenshot_saveto_assets(
        self,
        region,
        img_name="debug"
    ):

        save_dir = self.get_assets_dir(
            create=True
        )

        print(
            "[SAVE DIR]:",
            save_dir
        )
        path = save_dir / f"{img_name}.png"

        pag.screenshot(
            str(path),
            region=region
        )

        printl.B(
            f"Đã tạo [{img_name}.png] "
            f"và lưu tại {path}"
        )

        return {
            "path": str(path),
            "region": region,
            "size": (
                region[2],
                region[3]
            )
        }
    
    def screenshot_realtime(self, region, ext=".png",filename=None):

        global counter, last_ts
        letter = chr(rand(97,123))
        digit = rand(0, 101)
        with lock:
            ts = int(time.time())%10
            if ts == last_ts:
                counter += 1
            else:
                counter = 0
                last_ts = ts
            if filename is None:
                filename = f"{letter}_{ts}{digit}{ext}"
            path = os.path.join(self.assets_dir,filename)
            pag.screenshot(path, region=region)
            
            printl.B(f"Đã tạo [{filename}] và lưu tại: {path}")

            return {
                "path": path,
                "region": region,
                "size": (region[2], region[3])
            }

    def screenshot_saveto_subassets(self, region, name="img_name",subname="subname"):
        subdir = os.path.join(self.assets_dir,subname)
        os.makedirs(subdir, exist_ok=True)

        filename = f"{name}.png"
        path = os.path.join(subdir,filename)

        pag.screenshot(path, region=region)
        # printl.C(f"Đã tạo {filename}] và lưu tại {path}")
        
        return {
            "path": path,
            "region": region,
            "size": (region[2], region[3])
        }
    
    def screenshot_saveto_assets_help(self,img_name="img_name",size=(60,30)):
        reg = imgReg.region_from_pos(size=size)
        path_img = self.screenshot_saveto_assets(reg, f"{img_name}")
        p = imgCV2Find.find(path_img["path"])
        path_img = self.shrink_region_around(p)
        return path_img


    def shrink_region_around(self, pos, size=(60, 20)):
        x = y = None

        # -------------------------
        # dict
        # -------------------------
        if isinstance(pos, dict):

            if "pos" in pos:
                x, y = pos["pos"]

            elif "x" in pos and "y" in pos:
                x, y = pos["x"], pos["y"]

        # -------------------------
        # tuple/list
        # -------------------------
        elif isinstance(pos, (tuple, list)):

            # (x,y)
            if len(pos) == 2 and all(isinstance(v, (int, float)) for v in pos):
                x, y = pos

            # (x,y,w,h)
            elif len(pos) == 4 and all(isinstance(v, (int, float)) for v in pos):
                x, y = pos[0],pos[1]

            # (path,x,y)
            elif len(pos) >= 3:
                x, y = pos[1], pos[2]

        # -------------------------
        # string
        # -------------------------
        elif isinstance(pos, str):

            m = re.search(r"\((\d+)\s*,\s*(\d+)\)", pos)

            if m:
                x = int(m.group(1))
                y = int(m.group(2))

        # -------------------------
        # invalid
        # -------------------------
        if x is None or y is None:
            raise ValueError(f"Unsupported pos format: {pos}")

        w, h = size

        return (x - w // 2, y - h // 2, w, h)
    
    def auto_learn_template (self,name="img_name",size=(60,20),threshold=0.7,shrink_size=(54,18)):
        """
        🔥 Auto học template từ màn hình

        Steps:
        1. Lấy vùng quanh chuột
        2. Screenshot → assets/debug/
        3. Find lại template
        4. Shrink region quanh match
        5. Cache lại
        """

        print(f"\n[LEARN TEMPLATE] {name}")

        # ===== 1. Lấy vị trí chuột =====
        mx, my = imgPos.from_pos()
        print(f"[MOUSE] ({mx}, {my})")

        region = imgReg.region_from_pos(mx, my, size=size, debug=True)

        # ===== 2. Screenshot =====
        debug_dir = os.path.join(self.assets_dir, "debug")
        os.makedirs(debug_dir, exist_ok=True)

        path = os.path.join(debug_dir, f"{name}.png")
        pag.screenshot(path, region=region)

        print(f"[CAPTURED] {path}")

        # ===== 3. Find lại =====
        found = imgCV2Find.find(path, threshold=threshold, multi_scale=True)

        if not found:
            print("[❌ FAIL] Không match lại được template")
            return None

        print(f"[FOUND] {found}")

        # ===== 4. Shrink =====
        tight_region = self.shrink_region_around(found, size=shrink_size)
        print(f"[SHRINK] {tight_region}")

        # ===== 5. Cache =====
        key = f"{name}.png"
        scrCapture.cache[key] = found
        scrCapture.save_cache(found)

        print(f"[CACHED] {key} -> {found}")

        return {
            "path": path,
            "pos": found,
            "region": tight_region
        }
    
    def save_template_from_pos(self,name="auto.png", size=(60, 20)):
        x, y = imgPos.from_pos()
        w, h = size

        region = (x - w//2, y - h//2, w, h)

        path = os.path.join(self.assets_dir, name)
        pag.screenshot(path, region=region)

        print(f"[TEMPLATE SAVED] {path}")
        return path

# ====================================================== #
imgScrSave = ScreenShot()
# imgScrSave.screenshot_saveto_assets(imgReg.region_from_pos(size=(60,20)))
# ====================================================== #  
class CV2Finder(AutoBase):
    def __init__(self,monitor=1):
        self.sct = mss.MSS()
        self.monitor = self.sct.monitors[monitor]

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_dir = os.path.join(self.base_dir, "assets")

        # 🔥 cache file
        self.cache_file = os.path.join(self.base_dir, "pos_cache.json")
        self.cache = scrCapture.load_cache()
        

    def find(
        self,
        target,
        threshold=0.8,
        region=None,
        gray=True,
        multi_scale=True,
        debug=False,
        return_type="dict",
    ):

            # =====================================
            # normalize
            # =====================================

            data = unify.normalize_input(target)

            temp_path = data["path"]

            if not temp_path:
                return None

            # region priority:
            # param region > target region
            region = (
                unify.normalize_region(region)
                or data["region"]
            )

            # =====================================
            # capture
            # =====================================

            screen, monitor = scrCapture.capture(
                region,
                gray
            )

            temp = scrCapture.load_template(
                temp_path
            )

            if temp is None:
                return None

            # =====================================
            # gray
            # =====================================

            if gray and len(temp.shape) == 3:

                temp = cv2.cvtColor(
                    temp,
                    cv2.COLOR_BGR2GRAY
                )

            # =====================================
            # match
            # =====================================

            best_val = 0
            best_match = None

            scales = (
                (0.8, 1.0, 1.2)
                if multi_scale
                else [1.0]
            )

            for scale in scales:

                resized = cv2.resize(
                    temp,
                    None,
                    fx=scale,
                    fy=scale
                )

                # template bigger than screen
                if (
                    resized.shape[0] > screen.shape[0]
                    or
                    resized.shape[1] > screen.shape[1]
                ):
                    continue

                result = cv2.matchTemplate(
                    screen,
                    resized,
                    cv2.TM_CCOEFF_NORMED
                )

                _, max_val, _, max_loc = cv2.minMaxLoc(result)

                if max_val > best_val:

                    best_val = max_val

                    best_match = (
                        max_loc,
                        resized.shape[::-1]
                    )

            # =====================================
            # result
            # =====================================

            if best_val < threshold:
                return None

            (x, y), (w, h) = best_match

            left = x + monitor["left"]
            top = y + monitor["top"]

            center_x = left + w // 2
            center_y = top + h // 2

            result = {
                "path": temp_path,

                "x": center_x,
                "y": center_y,

                "w": w,
                "h": h,

                "left": left,
                "top": top,

                "pos": (
                    center_x,
                    center_y
                ),

                "rect": (
                    left,
                    top,
                    w,
                    h
                ),

                "region": region,

                "confidence": float(best_val)
            }

            # =====================================
            # debug
            # =====================================

            if debug:

                printl.C(result)

            # =====================================
            # return
            # =====================================

            return self.format_result(
                result,
                return_type
            )
    
    def format_result(self,data,return_type):
        mapping = {
            "dict": lambda:data,
            "tuple":lambda:data["pos"],
            "rect": lambda:data["rect"],
            "string":
            f"{data['path']}"
            f"{data['pos']}",
            "confidence":lambda:data["confidence"],
            "path":lambda:data["path"]
        }
        if return_type not in mapping:
            raise ValueError(f"Invalid return_type:" f"{return_type}")
        return mapping[return_type]()
    
    def smart_find(
            self, 
            temp_path,
            debug=False,
            return_type="dict",
        ):

        name = os.path.basename(temp_path)

        cached_region = scrCapture.get_cached_region(name)

        reg = self.find(
            temp_path,
            region=cached_region,
            return_type=return_type
        )
        # fallback full screen
        if not reg and cached_region:
            reg = self.find(
                temp_path,
                return_type=return_type
            )

        if reg:
            # self.cache[name] = imgScrSave.shrink_region_around(reg)
            self.cache[name] = reg
            scrCapture.save_cache(self.cache)
        if debug:
            printl.Y("----------------")
            printl.M(f'Temp_Path:"{reg['path']}"')
            printl.Y(f"Possion:{reg["pos"]}")
            printl.G(f"Region:{reg["region"]}")
            printl.hR(f"Rect:{reg["rect"]}")
            printl.C(f"Rand_Id[smart_find]: {id(self)}")

        return reg

    def smart_find_cv2_ocr(
        self,
        img_name=None,
        text=None,
        region=None,
        return_type="dict",
        threshold=0.7,
        rebuild=True,
        save_temp=False,
        save_cache=False,
        debug=False
    ):
        
        # =========================
        # normalize
        # =========================

        template_data = None
        template_path = None

        if img_name:

            template_data = unify.normalize_input(img_name)

            if template_data:

                # normalize_input return dict
                if isinstance(template_data, dict):

                    template_path = (
                        template_data.get("path")
                        or template_data.get("img_path")
                        or template_data.get("file")
                    )

                if template_path:

                    if not os.path.isabs(template_path):

                        template_path = os.path.join(
                            "assets",
                            template_path
                        )

                    template_path = os.path.abspath(
                        template_path
                    )

        # =========================
        # auto text fallback
        # =========================

        if not text and img_name:
            text = os.path.splitext(
                os.path.basename(img_name)
            )[0]

        text = text.replace("_", " ")

        # =========================
        # TEMPLATE EXISTS ?
        # =========================

        template_exists = (
            isinstance(template_path, str)
            and os.path.exists(template_path)
        )

        
        if template_exists:

            if debug:
                print("[TEMPLATE EXISTS]", template_path)

            # =========================
            # 1. CV2 FIRST
            # =========================

            pos = imgCV2Find.find(
                template_data if template_data else img_name,
                region=region,
                threshold=threshold,
                multi_scale=True,
                return_type=return_type
            )

            # =========================
            # CV2 HIT
            # =========================

            if pos:

                if debug:

                    printl.logt(
                        ("[CV2 HIT]", "G"),
                        (pos, "C")
                    )

                return pos

            # =========================
            # CV2 MISS -> OCR
            # =========================

            if debug:
                print("[CV2 MISS -> OCR]")

        else:

            if debug:
                print("[NO TEMPLATE -> OCR ONLY]")

        # =========================
        # OCR
        # =========================

        if not text:

            if debug:
                print("[NO OCR TEXT]")

            return None

        pos = imgOCRFind.find_text(
            text=text,
            region=region,
            debug=debug
        )

        # =========================
        # OCR HIT
        # =========================

        if pos:

            if debug:

                printl.logt(
                    ("[OCR HIT]", "Y"),
                    (pos, "C")
                )

            # =========================
            # rebuild/create template
            # =========================

            if rebuild and img_name:
                try:
                    if save_temp:
                        img_path=imgScrSave.save_template_from_pos(img_name+".png")
                    if save_cache:
                        imgCV2Find.smart_find(img_path)

                    if debug:

                        if template_exists:

                            print(
                                "[TEMPLATE REBUILT]",
                                img_name
                            )

                        else:

                            print(
                                "[TEMPLATE CREATED]",
                                img_name
                            )

                except Exception as e:

                    if debug:

                        print(
                            "[SAVE TEMPLATE ERROR]",
                            e
                        )

                return {"pos":pos,"temp_cache":img_path}

        # =========================
        # OCR FAIL
        # =========================

        if debug:
            print("[OCR FAIL]")

        return None

    def smart_find_cv2_text(
        self,
        img_name,
        region=None,
        threshold=0.7,
        return_type="dict",
        debug=False,
        save_temp=False,
        assets_dir=None
    ):

        # =======================
        # normalize path
        # =======================

        img_path = unify.normalize_input(img_name)

        # =======================
        # 1. try CV2
        # =======================

        if img_path:

            pos = imgCV2Find.find(
                img_path,
                region=region,
                threshold=threshold,
                multi_scale=True,
                return_type=return_type
            )

            if pos:

                if debug:
                    printl.logt(
                        ("[CV2 HIT]", "G"),
                        (pos, "C")
                    )

                return pos

            if debug:
                print("[CV2 MISS]", img_name)

        else:

            if debug:
                print("[NO TEMPLATE]", img_name)

        # =======================
        # 2. OCR fallback
        # =======================

        # auto convert:
        # go_live.png -> go live

        text = os.path.splitext(
            os.path.basename(img_name)
        )[0]

        text = text.replace("_", " ")

        if debug:
            print("[OCR SEARCH]:", repr(text))
        pos = imgOCRFind.find_text(
            text=text,
            region=region,
            debug=debug,
            save_temp=save_temp,
            assets_dir=assets_dir
        )

        if pos:

            if debug:
                printl.logt(
                    ("[OCR HIT]", "Y"),
                    (pos, "C")
                )

            return pos

        # =======================
        # all fail
        # =======================

        if debug:
            print("[SMART FIND FAILED]")

        return None
    
# ====================================================== #
imgCV2Find = CV2Finder()

# ====================================================== #

def auto_learn_template_v2(name="auto", tries=3):
    for i in range(tries):
        print(f"\n[TRY {i+1}]")

        res = imgScrSave.auto_learn_template(name=f"{name}_{i}")

        if res:
            return res

        time.sleep(0.5)

    print("[❌ TOTAL FAIL]")
    return None

# ====================================================== #
# ====================================================== #

# imgOCRFind.find_text(
#     "Go Live",
#     imgReg.region_from_pos(size=(60, 20)),  
#     debug=True,
#     save_temp=True
# ) # -> save_temp_path: img_name = hover_current_text
# ====================================================== #

# imgCV2Find.smart_find_cv2_ocr(
#     "py_thon",
#     save_temp=True,
#     save_cache=True,
#     debug=True
# ) # -> "py_thon" vs save_temp=True => py_thon.png; save_cache=True => lưu vào pos_cache.json
# ====================================================== #

# imgCV2Find.smart_find_cv2_ocr("python.png",debug=True) # -> print_template: python.png
# ====================================================== #

# imgScrSave.screenshot_saveto_assets(
#     imgReg.region_from_pos(size=(60,20)),
#     img_name="script"
# ) # CV2: -> tạo script.png
# ====================================================== #

# imgScrSave.screenshot_saveto_assets_help(
#     "icon_run",size=(40,45)
# ) # -> tạo hình ảnh nút ▶ [Run Code] => icon_run.png
# ====================================================== #
# imgOCRFind.find_text(
#     "Go Live",
#     region=imgReg.region_from_pos(
#         size=(60,20)
#     ),
#     save_temp=True,

# )


# ====================================================== #

# ====================================================== #
# pos =imgReg.region_from_pos(size=(150,70))
# printl(pos)
# imgCV2Find.smart_find("go_liv.png",debug=True)

