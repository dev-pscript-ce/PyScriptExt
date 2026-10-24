import sys,os,time, itertools, threading,json ,shutil
# Tắt __pycache__
sys.dont_write_bytecode = True
from pathlib import Path

from datetime import datetime
from colorama import init
init()

def add_root(level: int = 2):
    ROOT_DIR = Path(__file__).resolve().parents[level]

    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))

    return ROOT_DIR
add_root()

RESET = "\x1b[0m"

ANSI_ALIAS = {
    "rR": "red",
    "rG": "green",
    "rO": "orange",
    "rY": "yellow",
    "rY1": "yellow1",
    "rB": "blue",
    "rM": "mangenta",
    "rC": "cyan",
    "rPi": "pink",
    "rPu": "purple",
    "rW": "white",
    "rA": "gray",
    "rS": "sky",
    "rL": "lime"
}

ANSI = {
    "R":31,"G":32,"Y":33,"B":34,"M":35,"C":36,"W":37,"A":90,
    "bR":41,"bG":42,"bY":43,"bB":44,
    "bM":45,"bC":46,"bW":47,

    # style
    "b":1,     # bold
    "d":2,     # dim
    "i":3,     # italic
    "u":4,     # underline

    # reset riêng
    "rb":22,
    "ri":23,
    "ru":24,

    # hex:
    "hR": "#ff0000",
    "hG": "#00ff00",
    "hP":"#ff00aa",
    "h8":"#888888",
    "ha":"#aaaaaa",
    "discord": "#5865F2",
    "github":  "#24292e",
    "warn": "#ffcc00",

    # rgb:
    "red":(255, 0, 0),
    "green": (0, 255, 0),
    "yellow": (255, 255, 0),
    "yellow1": (255, 220, 120),
    "blue": (0, 0, 255),
    "magenta": (220, 120, 255),
    "orange": (255,120,0),
    "pink": (255,192,203),
    "purple": (128, 0, 128),
    "cyan": (120, 220, 255),
    "white": (255, 255, 255),
    "gray": (0, 0,0),
    "sky": (0,200,255),
    "lime": (120,255,0),
}

ANSI_PRESET = {

    "glass": {
        "fg": "#00d4ff",
        "bg": "#111111",
        "styles": ["b", "i"]
    },

    "danger": {
        "fg": "#ff4444",
        "styles": ["b"]
    },

    "warn": {
        "fg": "#ffcc00",
        "bg": "#332200",
    },

    "success": {
        "fg": (0,255,120),
        "styles": ["b"]
    },
    "title":{
        "fg":"#00d4ff",
        "styles":["b","u"]
    },
    "subtitle":{
        "fg": "#888888",
        "styles": ["i"]
    }
}

class Ansi:

    def __init__(self, codes=None):
        self.codes = codes or []

    # =========================
    # chain ANSI
    # =========================
    def __getattr__(self, name):

        if name in ANSI_ALIAS:
            name = ANSI_ALIAS[name]

        if name in ANSI:
            value = ANSI[name]
            # ===== int => ANSI =====
            if isinstance(value,int):
                return self.ansi_basic(value)
            # ===== tuple => RGB =====
            if (
                isinstance(value, tuple)
                and len(value) == 3
                and all(isinstance(x, int) for x in value)
            ):
                return self.rgb(*value)
            
            if (
                isinstance(value,str)
                and value.startswith("#")
            ):
                return self.hex(value)
            
        if name in ANSI_PRESET:

            value = ANSI_PRESET[name]

            # copy current chain
            obj = Ansi(self.codes.copy())

            # =========================
            # foreground
            # =========================
            obj = self.apply_color(
                obj,
                value.get("fg")
            )

            # =========================
            # background
            # =========================
            obj = self.apply_color(
                obj,
                value.get("bg"),
                bg = True
            )

            # =========================
            # styles
            # =========================
            for style in value.get("styles", []):

                obj = getattr(obj, style)

            return obj
        raise AttributeError(name)
        
    def apply_color(self, obj, value, bg=False):

        if isinstance(value, tuple):

            return (
                obj.bg_rgb(*value)
                if bg else
                obj.rgb(*value)
            )

        if isinstance(value, str) and value.startswith("#"):

            return (
                obj.bg_hex(value)
                if bg else
                obj.hex(value)
            )

        return obj

    def ansi_basic(self, codes):
        return Ansi(self.codes + [f"\x1b[{codes}m"])

    # =========================
    # RGB foreground
    # =========================
    def rgb(self, r, g, b):
        return Ansi(
            self.codes + [f"\x1b[38;2;{r};{g};{b}m"]
        )

    # =========================
    # RGB background
    # =========================
    def bg_rgb(self, r, g, b):
        return Ansi(
            self.codes + [f"\x1b[48;2;{r};{g};{b}m"]
        )

    @staticmethod
    def _hex_to_rgb(value):

        value = value.lstrip("#")

        if len(value) == 3:
            value = "".join(c * 2 for c in value)

        if len(value) != 6:
            raise ValueError(
                f"Invalid HEX color: #{value}"
            )

        return (
            int(value[0:2], 16),
            int(value[2:4], 16),
            int(value[4:6], 16),
        )

    # =========================
    # HEX foreground
    # =========================
    def hex(self, value):
        return self.rgb(*self._hex_to_rgb(value))

    # =========================
    # HEX background
    # =========================
    def bg_hex(self, value):
        return self.bg_rgb(*self._hex_to_rgb(value))

    # =========================
    # render
    # =========================
    def __call__(self, *args):

        text = " ".join(map(str, args))

        prefix = "".join(self.codes)

        return f"{prefix}{text}{RESET}"


ansi = Ansi()

# ansi.rO = ansi.rgb(255,120,0)
# ===================================================

def resolve_value(v, opts=None, depth=0):

    if opts is None:
        opts = {}

    multiline = opts.get("multiline", False)
    indent = opts.get("indent", 2)
    kv = opts.get("kv", False)

    pad = lambda n: " " * n

    if callable(v):
        return resolve_value(v(), opts, depth)

    if v is None:
        return ""

    if isinstance(v, (str, int, float, bool)):
        return str(v)

    if isinstance(v, list):

        if not multiline:
            return "\n\n".join(resolve_value(x, opts, depth) for x in v)

        return "\n\n".join(
            pad(depth * indent) + resolve_value(x, opts, depth + 1)
            for x in v
        )

    if isinstance(v, dict):

        if not multiline:
            resolved = {k: resolve_value(val, opts, depth) for k, val in v.items()}
            return json.dumps(resolved)

        lines = []

        for k, val in v.items():

            value = resolve_value(val, opts, depth + 1)

            if kv:
                lines.append(f"{k}={value}")
            else:
                formatted = value.replace(
                    "\n",
                    "\n" + pad((depth + 1) * indent)
                )

                lines.append(
                    pad(depth * indent) + f"{k}: {formatted}"
                )

        return "\n".join(lines)

    return str(v)
# ===================================================

class Logger_Config:
    timeMode = "local"

def timestamp(mode="local"):
    t = datetime.utcnow() if mode == "utc" else datetime.now()
    return t.strftime("%Y-%m-%d %H:%M:%S")


def make_prefix(prefix):
    return f"[{prefix}]" if prefix else ""

# ===================================================

def format_msg(color, prefix, *args, b=False):
    time_str = ansi.G(f"[{timestamp()}]")
    prefix_str = ansi.C(f"[{prefix}]") if prefix else ""

    msg = " ".join(map(str, args))
    msg = getattr(ansi, color)(msg)

    if b:
        msg = ansi.b(msg)

    return " ".join(filter(None, [time_str, prefix_str, msg]))

def multi_char(char="=",n=10):
    c = char*n
    return printl.A(c)

# ================================================================

def colorize_json(obj, indent=2):
    try:
        parsed = json.dumps(obj, indent=indent, ensure_ascii=False)
    except TypeError:
        return str(obj)

    result = []
    in_string = False
    key_mode = True

    i = 0
    while i < len(parsed):
        ch = parsed[i]

        if ch == '"':
            j = i + 1
            while j < len(parsed):
                if parsed[j] == '"' and parsed[j-1] != "\\":
                    break
                j += 1

            token = parsed[i:j+1]

            if key_mode:
                result.append(ansi.C(token))  # key
            else:
                result.append(ansi.Y(token))  # string value

            i = j + 1
            continue

        elif ch in "0123456789":
            j = i
            while j < len(parsed) and parsed[j] in "0123456789.":
                j += 1
            result.append(ansi.G(parsed[i:j]))  # number
            i = j
            continue

        elif parsed.startswith("true", i) or parsed.startswith("false", i):
            val = "true" if parsed.startswith("true", i) else "false"
            result.append(ansi.M(val))
            i += len(val)
            continue

        elif parsed.startswith("null", i):
            result.append(ansi.A("null"))
            i += 4
            continue

        elif ch == ":":
            key_mode = False
            result.append(ch)

        elif ch == ",":
            key_mode = True
            result.append(ch)

        else:
            result.append(ch)

        i += 1

    return "".join(result)

# ==================================================================

class _PrintlProxy:
    def __init__(self, chain):
        self.chain = chain

    def __getattr__(self, name):
        return _PrintlProxy(getattr(self.chain, name))

    def __call__(self, *args):
        printl._print(*args, chain=self.chain)
    
    def logt(self, *args, level="LOG", name=""):
        printl.logt(*args, chain=self.chain, level=level,name=name)

    def json(self, data):
        printl.json(data, chain=self.chain)

    def pretty(self, *args, **opts):
        printl.pretty(*args, chain=self.chain, **opts)

    def table(self, rows):
        printl.table(rows, chain=self.chain)

# ==================================================================

# Helper for _print() and _build_text():
def build_parts(args,chain=None):
    parts = []

    for a in args:
        if isinstance(a, tuple) and len(a) == 2:
            text, style = a
            # RGB:
            if (
                isinstance(style, tuple)
                and len(style) == 3
                and all(isinstance(x, int) for x in style)
            ):
                style = ansi.rgb(*style)
            # HEX:
            elif (
                isinstance(style, str)
                and style.startswith("#")
            ):
                style = ansi.hex(style)
            #  ansi name:
            elif isinstance (style, str):
                style = getattr (ansi,style)

            parts.append(
                style(str(text))
            )
        else:
            text = str(a)
            parts.append(
                chain(text) if chain else text
            )
    return " ".join(parts)

class Printl:
    def __init__(self):
        self.mode = "json"

    # ===== chain =====
    def __getattr__(self, name):
        return _PrintlProxy(getattr(ansi, name))

    # ===== smart print =====
    def __call__(self, *args):
        self._print(*args)

    def _print(self, *args, chain=None):

        # =========================================
        # auto format khi chỉ có 1 arg
        # =========================================
        if len(args) == 1:

            v = args[0]

            # ===== auto table =====
            if isinstance(v, list) and v and isinstance(v[0], dict):
                self.table(v, chain=chain)
                return

            # ===== auto dict =====
            if isinstance(v, dict):

                if self.mode == "json":
                    self.json(v, chain=chain)
                else:
                    self.pretty(v, multiline=True, chain=chain)

                return
        final = build_parts(args,chain)
        print(final)
        return final
    
    # ===== JSON =====
    def json(self, data, chain=None):
        text = colorize_json(data)
        print(chain(text) if chain else text)

    # ===== PRETTY =====
    def pretty(self, *args, chain=None, **opts):
        text = " ".join(resolve_value(a, opts) for a in args)
        print(chain(text) if chain else text)

    # ===== TABLE =====
    def table(self, rows, color=None, chain=None):
        if not rows:
            print("(empty)")
            return

        headers = list(rows[0].keys())
        widths = {h: len(h) for h in headers}

        for r in rows:
            for h in headers:
                widths[h] = max(widths[h], len(str(r[h])))

        def fmt(text, is_header=False):
            if chain:
                return chain(text)
            if color:
                return getattr(ansi, color)(text)
            return text

        # ===== special: 1 column =====
        if len(headers) == 1:
            h = headers[0]
            width = widths[h]

            print(fmt(h))
            print(fmt("-" * width))

            for r in rows:
                print(fmt(str(r[h])))
            return

        # ===== normal table =====
        line = " | ".join(fmt(h.ljust(widths[h]), True) for h in headers)
        sep  = "-+-".join("-"*widths[h] for h in headers)

        print(line)
        print(sep)

        for r in rows:
            print(" | ".join(
                fmt(str(r[h]).ljust(widths[h]))
                for h in headers
            ))

    # ===== LOG LEVEL =====
    def log(self, *args):
        self._print(*args, chain=ansi.W)

    def log_tamp(self, t_color, level_color, name_color, text_color, level, name="", *msg):
        t = datetime.now().strftime("%H:%M:%S")
        text = " ".join(map(str, msg))

        t_str = ansi.b.__getattr__(t_color)(f"[{t}]")
        level_str = ansi.b.__getattr__(level_color)(f"[{level}]")
        name_str = ansi.b.__getattr__(name_color)(name) if name else ""
        text_str = ansi.b.__getattr__(text_color)(text)

        print(f"{t_str} {level_str} {name_str} {text_str}")
    
    def logt(self, *args, chain=None, level="Debug", name=""):
        t = datetime.now().strftime("%H:%M:%S") 
        text = " ".join(map(str, args))
        # ===== fixed color (không bị override) =====
        t_str = ansi.C(f"[{t}]")
        level_str = ansi.Y(f"[{level}]:")
        name_str = ansi.G(name) if name else ""
        # ===== chỉ apply chain vào text =====
        text_str = chain(text) if chain else text
         # ===== xử lý từng arg =====
        parts = []

        for a in args:

            if isinstance(a, tuple) and len(a) == 2:

                val, style = a

                if isinstance(style, str):
                    style = getattr(ansi, style)

                parts.append(style(str(val)))

            else:

                text = str(a)

                parts.append(chain(text) if chain else text)

        text_str = " ".join(parts)
        print(f"{t_str} {level_str} {name_str} {text_str}")

    def info(self, *args):
        self._print(*args, chain=ansi.C)

    def warn(self, *args):
        self._print(*args, chain=ansi.Y)

    def error(self, *args):
        self._print(*args, chain=ansi.R)
# ==================================================================

class _InputlProxy:
    def __init__(self, chain):
        self.chain = chain

    def __getattr__(self, name):
        return _InputlProxy(getattr(self.chain, name))

    def __call__(self, *args):
        return inputl._input(*args, chain=self.chain)

    def json(self, data):
        return inputl.json(data, chain=self.chain)

    def pretty(self, *args, **opts):
        return inputl.pretty(*args, chain=self.chain, **opts)

    def table(self, rows):
        return inputl.table(rows, chain=self.chain)
    
    def confirm(self, text="Confirm?", default=True):
        return inputl.confirm(text=text, default=default, chain=self.chain)
# ==================================================================

class Inputl:
    def __init__(self, mode="text"):
        self.mode = mode

    # ===== chain =====
    def __getattr__(self, name):
        return _InputlProxy(getattr(ansi, name))

    # ===== call =====
    def __call__(self, *args):
        return self._input(*args)

    # ===== core =====
    def _input(self, *args, chain=None):
        text = self._build_text(*args, chain=chain)
        return input(text)

    # ===== build text (tách riêng giống outlog) =====
    def _build_text(self, *args, chain=None):
        if not args:
            return ""
        if len(args) == 1:
            v = args[0]

            # ===== dict =====
            if isinstance(v, dict):
                if self.mode == "json":
                    text = self._format_json(v)
                else:
                    text = self._format_pretty(v)
                return self._apply_chain(text, chain)
            
            # ===== list[dict] => table string =====
            if isinstance(v, list) and v and isinstance(v[0], dict):
                return self._format_table(v, chain) # ⚠️ đã chain trong table rồi

        # ===== fallback =====
        return build_parts(args, chain)

    # ===== helpers =====
    def _apply_chain(self, text, chain):
        return chain(text) if chain else text

    # ===== JSON =====
    def _format_json(self, data):
        try:
            return colorize_json(data)
        except:
            import json
            return json.dumps(data, ensure_ascii=False)

    def json(self, data, chain=None):
        text = self._format_json(data)
        return input(self._apply_chain(text, chain))

    # ===== PRETTY =====
    def _format_pretty(self, data):
        return resolve_value(data, {"multiline": True})

    def pretty(self, *args, chain=None, **opts):
        text = " ".join(resolve_value(a, opts) for a in args)
        return input(self._apply_chain(text, chain))

    # ===== TABLE (fix: return string instead of print) =====
    def _format_table(self, rows, chain=None):
        if not rows:
            return "(empty)"

        headers = list(rows[0].keys())
        widths = {h: len(h) for h in headers}

        for r in rows:
            for h in headers:
                widths[h] = max(widths[h], len(str(r[h])))

        def fmt(text):
            return self._apply_chain(text, chain)

        # ===== 1 column =====
        if len(headers) == 1:
            h = headers[0]
            width = widths[h]

            lines = [
                fmt(h),
                fmt("-" * width)
            ]

            for r in rows:
                lines.append(fmt(str(r[h])))

            return "\n".join(lines)

        # ===== multi column =====
        line = " | ".join(fmt(h.ljust(widths[h])) for h in headers)
        sep  = "-+-".join("-"*widths[h])

        lines = [line, sep]

        for r in rows:
            lines.append(" | ".join(
                fmt(str(r[h]).ljust(widths[h]))
                for h in headers
            ))

        return "\n".join(lines)

    def table(self, rows, chain=None):
        text = self._format_table(rows, chain)
        return input(text)
    
    def confirm(self, text="Confirm?", default=True, chain=None):
        yes = ("y", "yes")
        no = ("n" ,"no")

        hint = "Y/n" if default else "y/N"
        
        while True:
            prompt = f"{text} ({hint})"
            if chain:
                prompt = chain(prompt)
            ans = inputl.Y(prompt).strip().lower()

            if ans == "":
                return default
            
            if ans in yes:
                return True
            
            if ans in no:
                return False
            err = "Nhập y/n"
            printl.error(err) if chain else err

    def ask_opt(question, options):
        opts = "".join(options)
        while True:
            ans = inputl(f"{question} ({opts}): ").lower()
            if ans in options:
                return ans

    def select(self, option, multi = False):
        s = Select(options=option,multi=multi)
        return s.run()

# ==================================================================
# ===== instance =====
inputl,readl = (Inputl(),Inputl())
printl,writel = (Printl(),Printl())

# ==================================================================

class WriteTamp:
    def __getattr__(self, color):
        def fn(prefix, *args):
            print(format_msg(color, prefix, *args))
        def b(prefix, *args):
            print(format_msg(color, prefix, *args, b=True))

        fn.b = b
        return fn
# ==================================================================
# write_tamp,writet =(WriteTamp(),WriteTamp())
# printl.log_tamp("Y","G","B","C","Node","Python","logtamp")
# printl.logt(
#     ("Error:", ansi.R),
#     ("file not found","G"),
#     ("-> fallback default",ansi.Y),
#     ("Tin",ansi.M.i)
# )
# printl.logt(("Node","Y"),("Python","G"),("Tin","M"))
# ==================================================================

SPINNER = ["|", "/", "-", "\\"]

# =========================
# THEME
# =========================
THEMES = {
    "dark": {
        "text": "\x1b[32m",
        "muted": "\x1b[90m",
        "percent":"\x1b[36m",
        "eta":"\x1b[31m",
    },
    "light": {
        "text": "\x1b[32m",
        "muted": "\x1b[30m",
        "percent":"\x1b[36m",
        "eta":"\x1b[31m",
    }
}

def rgb_color(percent):
    if percent < 0.5:
        g = int(255 * (percent / 0.5))
        r = 255
    else:
        g = 255
        r = int(255 * (1 - (percent - 0.5) / 0.5))
    return f"\x1b[38;2;{r};{g};0m"

# =========================
# PROGRESS BAR
# =========================
class ProgressBar:
    def __init__(self, total, name="", width=None, theme="dark", on_done=None):
        self.total = max(total, 1)
        self.name = name
        self.theme = THEMES.get(theme, THEMES["dark"])
        self.on_done = on_done

        self.current = 0
        self.start_time = time.time()
        self.spinner_idx = 0

        self.paused = False
        self._pause_time = 0

        self.width = width  # None = auto

    def pause(self):
        if not self.paused:
            self.paused = True
            self._pause_time = time.time()

    def resume(self):
        if self.paused:
            paused_duration = time.time() - self._pause_time
            self.start_time += paused_duration
            self.paused = False

    def _eta(self, speed):
        if speed <= 0:
            return "--:--"
        remain = self.total - self.current
        sec = remain / speed
        m, s = divmod(int(sec), 60)
        return f"{m:02}:{s:02}"

    def _calc_width(self):
        if self.width:
            return self.width

        term_width = shutil.get_terminal_size((80, 20)).columns
        return max(10, term_width - 50)  # auto fit

    def render(self):
        percent = min(self.current / self.total, 1)

        width = self._calc_width()
        filled = int(width * percent)
        bar = "█" * filled + " " * (width - filled)

        color = rgb_color(percent)

        elapsed = time.time() - self.start_time
        speed = self.current / elapsed if elapsed > 0 else 0

        spinner = SPINNER[self.spinner_idx % len(SPINNER)]
        self.spinner_idx += 1

        line = (
            f"{self.theme['text']}{self.name}\x1b[0m "
            f"{spinner} "
            f" [{color}{bar}\x1b[0m]"
            f"{self.theme['percent']}| {int(percent*100):3d}% "
            f"{self.theme['muted']}| {speed:6.2f} it/s "
            f"{self.theme['eta']}| ETA {self._eta(speed)}\x1b[0m "
        )

        return line

    def tick(self, step=1):
        if self.paused:
            return

        self.current += step

        if self.current >= self.total:
            self.current = self.total
            if self.on_done:
                self.on_done(self)

    def is_done(self):
        return self.current >= self.total
def done(bar):
    printl.G(f"\n✔ Done: {bar.name}")


# =========================
# MULTI MANAGER
# =========================
class MultiProgress:
    def __init__(self, fps=10):
        self.bars = []
        self.running = False
        self.fps = fps

        self._last_lines = []
        self._lock = threading.Lock()

    def add(self, bar):
        self.bars.append(bar)

    def start(self):
        self.running = True
        print()  # reserve space
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self.running = False
        sys.stdout.write(f"\x1b[{len(self.bars)}B")  # move cursor xuống
        sys.stdout.write("\n")

    def _loop(self):
        while self.running:
            self.render()
            time.sleep(1 / self.fps)

    def render(self):
        with self._lock:
            lines = [b.render() for b in self.bars]

            # lần đầu: in full
            if not self._last_lines:
                for line in lines:
                    sys.stdout.write(line + "\n")
                self._last_lines = lines
                sys.stdout.flush()
                return

            # diff render
            for i, (new, old) in enumerate(zip(lines, self._last_lines)):
                if new != old:
                    # move cursor tới dòng i
                    sys.stdout.write(f"\x1b[{len(lines)-i}F")  # lên đúng vị trí
                    sys.stdout.write("\r" + new)
                    sys.stdout.write(f"\x1b[{len(lines)-i}E")  # xuống lại

            self._last_lines = lines
            sys.stdout.flush()
# ==================================================================

# ===== platform key reader =====

if os.name== "nt":
    try:
        from pscript.helpers.select_win import read_key
    except ImportError:
        read_key = None
else:
    from select_unix import read_key

# ===== Select =====
class Select:

    def __init__(self, options=[], multi=False, pointer="❯", page_size=8):
        self.options = options or []
        self.multi = multi
        self.pointer = pointer
        self.page_size = page_size

        self.index = 0
        self.selected = set()
        self.query = ""
        self.offset = 0
        self._last_lines = 0
     
    def _filter(self):
        if not self.query:
            return self.options
        q = self.query.lower()
        return [o for o in self.options if q in str(o).lower()]
    
    def _window(self,data):
        if self.index < self.offset:
            self.offset = self.index
        elif self.index >= self.offset + self.page_size:
            self.offset = self.index - self.page_size + 1

        return data[self.offset:self.offset + self.page_size]

    # ===== clear line =====
    def _clear(self):
        for _ in range(self._last_lines):
            sys.stdout.write("\033[F\033[K")  # lên + clear line

    def _render(self):
        
        self._clear()

        data = self._filter()
        if not data:
            printl.G(f"Search: {self.query}")
            printl.R("(No result)")
            self._last_lines = 2
            return 
        
        if self.index >= len(data):
            self.index = len(data) - 1

        win = self._window(data)
        lines = []

        # ===== build UI (KHÔNG print ngay) =====
        lines.append(f"Search: {self.query}")
        lines.append("")

        for i, opt in enumerate(win):
            real_i = self.offset + i

            prefix = "❯" if i == self.index else " "

            mark = ""
            if self.multi:
                mark = "[x]" if opt in self.selected else "[ ]"

            line = f"{prefix} {mark} {opt}" if self.multi else f"{prefix} {opt}"

            if real_i == self.index:
                line = ansi.b.C(line)

            # highlight current
            if self.query:
                line = line.replace(self.query,ansi.Y(self.query))

            lines.append(line)



        # scroll indicator
        if len(data) > self.page_size:
            lines.append(
                f"({self.offset+1}-{self.offset+len(win)}/{len(data)})"
            )

        print("\n".join(lines))
        sys.stdout.flush()

        self._last_lines = len(lines)

    def run(self):
        while True:
            self._render()
            key = read_key()

            filtered = self._filter()

            if self.index >= len(filtered):
                self.index = 0

            if not filtered:
                continue

            if key == "UP":
                self.index = (self.index - 1) % len(filtered)

            elif key == "DOWN":
                self.index = (self.index + 1) % len(filtered)

            elif key == "SPACE" and self.multi:
                val = filtered[self.index]
                if val in self.selected:
                    self.selected.remove(val)
                else:
                    self.selected.add(val)

            elif key == "ENTER":
                if self.multi:
                    return list(self.selected)
                return filtered[self.index]

            elif key == "BACKSPACE":
                self.query = self.query[:-1]
                self.index = 0

            elif len(key) == 1:
                self.query += key
                self.index = 0

select = Select()
# ========================================================
# Helpers hỗ trợ màu [option has or not has]
def c(text, style):

    #RGB:
    if(
        isinstance(style,tuple)
        and len(style)==3
        and all(isinstance(x,int) for x in style)
    ): 
        return ansi.rgb(*style) (text)
    #HEX:
    if(
        isinstance(style, str)
        and style.startswith("#")
    ):
        return ansi.hex(style)(text)
    # ANSI name:
    if isinstance(style, str):
        return getattr(ansi,style)(text)
    # ansi.R.b ...
    return style(text)

def multi_char(
        char:str = "",
        color_char:Ansi | str | tuple[int, int, int]=None,
        n:int = 0
    ):
    if color_char is None:
        color_char = ansi.ansi_basic(90)
    return printl(char*n,color_char)

# ========================================================

def banner(
    title="",
    color_title: Ansi | str | tuple[int, int, int] = None,
    char: str = "",
    color_char: Ansi | str | tuple[int, int, int] = None,
    n: int = 1,
):
    if color_title is None:
        color_title = ansi.ansi_basic(33)

    if color_char is None:
        color_char = ansi.ansi_basic(90)

    line_len = len(char) * n

    # =========================================
    # Validate
    # =========================================

    if title and line_len <= len(title):
        return printl(
            (
                f"Banner error: "
                f"length of char*n ({line_len}) "
                f"must be greater than title length ({len(title)})",
                ansi.ansi_basic(31),
            )
        )

    # =========================================
    # No title
    # =========================================

    if not title:
        return printl(
            (char * n, color_char),
        )

    # =========================================
    # Calculate padding
    # =========================================

    padding = line_len - len(title)

    size = padding // 2

    left = size
    right = size

    # =========================================
    # Print
    # =========================================

    return printl(
        (char * left, color_char),
        (title, color_title),
        (char * right, color_char),
    )
