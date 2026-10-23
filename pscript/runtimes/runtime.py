import sys
sys.dont_write_bytecode = True

from pathlib import Path

from resolve_path.find_file_root_args import find_file

from pscript.helpers.color import(
    ansi,
    banner,
    Printl,
    Inputl,
    Select,
    )


from ..engines.engine_api import Engine
from ..engines.stack import Stack
from ..modules import (
    CV2Module,
    OCRModule,
    STDModule,
    CreateFileModule
)

engine = Engine()
printl = Printl()
inputl = Inputl()
select = Select()

class Runtime:

    def __init__(self, project_root=None,python_root=None):

        # Root của project DSL đang chạy
        self.project_root = (
            Path(project_root).resolve()
            if project_root is not None
            else None
        )
        self.python_root = (
            Path(python_root).resolve()
            if python_root is not None
            else None
        )

        # # Assets của project DSL
        # self.assets_dir = (
        #     self.project_root / "assets"
        #     if self.project_root is not None
        #     else None
        # )

        # Stack file .ps đang chạy/import
        self.file_stack = []

        # Core Engine
        self.engine = Engine()

        # Python modules
        self.modules = {}

        # Imported DSL modules (.ps)
        self.script_modules = {}

        # Built-in functions
        self.builtins = {}

        self.register_builtin()
        self.register_modules()


    def register(self, name, obj):
        self.builtins[name] = obj

    def register_module(self, name, obj):
        self.modules[name] = obj

    def get_module(self,name):
        return self.modules.get(name)
    
    def get(self, name):
        return self.builtins.get(name)

    def register_builtin(self):

        self.register("select",select)
        self.register("banner",banner)

        self.register("ansi",ansi)
        self.register("print",printl)
        self.register("input",inputl)
        
        self.register("ansi_basic",ansi.ansi_basic)
        self.register("rgb",ansi.rgb)
        self.register("hex",ansi.hex)
        self.register("bg_rgb",ansi.bg_rgb)

        self.register("writel", self.engine._writel)
        self.register("printl", self.engine._printl)
        self.register("inputl", self.engine._inputl)
        self.register("ask_option", self.engine._ask_option)

        self.register("Write", self.engine._write)
        self.register("Type_Write", self.engine._type_write)
        self.register("Press", self.engine._press)
        self.register("Hot_Key", self.engine._hotkey)
        self.register("Set_Interval",self.engine._set_interval)
        self.register("Key_Down", self.engine._key_down)
        self.register("Key_Up", self.engine._key_up)
        self.register("Click", self.engine._click)
        self.register("Double_Click", self.engine._double_click)
        self.register("Sleep", self.engine._sleep)
        self.register("Move_Rel", self.engine._move_rel)
        self.register("Move_To_Img", self.engine._move_to_img)
        
        self.register("Find_Text", self.engine._find_text)
        self.register("Click_Text", self.engine._click_text)
        self.register("Wait_Text", self.engine._wait_text)

        self.register("Find_Img", self.engine._find_img)
        self.register("Click_Img", self.engine._click_img)
        self.register("Smart_Find", self.engine._smart_find)
        self.register("Smart_Click", self.engine._smart_click)
        self.register("Wait_Img", self.engine._wait_img)
        # ------------------------------------------------ #

        self.register("create_file",self.engine._create_file)
        self.register("range", self.engine._range)
        self.register("push", self.engine._push)
        self.register("pop", self.engine._pop)
        self.register("split", self.engine._split)
        self.register("join", self.engine._join)
        self.register("error", self.engine._error)
        self.register("stack", Stack)

        self.register("set", set)
        self.register("list", list)
        self.register("dict", dict)
        self.register("tuple", tuple)

        self.register("len", len)
        self.register("int", int)
        self.register("float", float)
        self.register("str", str)
        self.register("bool", bool)

    def register_modules(self):

        self.register_module(
            "cv2",
            CV2Module(self.engine)
        )

        self.register_module(
            "ocr",
            OCRModule(self.engine)
        )

        self.register_module(
            "std",
            STDModule(self.engine)
        )

        self.register_module(
            "cre",
            CreateFileModule(self.engine)
        )

    def load_script(self, module):

        from ..scanners.scanner import Scanner
        from ..parsers.parser import Parser
        from ..tokens.scope import Scope
        from ..interpreters.interpreter import Interpreter
        from ..asts.module_obj import ModuleObject

        path = self.resolve_import(module)

        # cache
        
        if path in self.script_modules:
            return self.script_modules[path]

        self.file_stack.append(path)

        try:

            source = path.read_text(encoding="utf8")

            scanner = Scanner(source)
            tokens = scanner.scan()

            parser = Parser(tokens)
            tree = parser.parse()

            scope = Scope()

            interpreter = Interpreter(
                runtime=self,
                scope=scope,
            )

            interpreter.visit(tree)

            module_obj = ModuleObject(scope)

            self.script_modules[path] = module_obj

            return module_obj

        finally:
            self.file_stack.pop()

    def resolve_import(self, module):

        path = Path(module)

        #
        # absolute
        #
        if path.is_absolute():
            return path.resolve()

        #
        # relative với file hiện tại
        #
        if self.file_stack:

            base = self.file_stack[1].parent

            candidate = (base / path).resolve()

            if candidate.exists():
                return candidate

        #
        # relative với project root
        #
        if self.project_root is not None:

            candidate = (self.project_root / path).resolve()

            if candidate.exists():
                return candidate

        #
        # cuối cùng dùng find_file()
        #
        return find_file(
            module,
            start=self.project_root or Path.cwd()
        )

    def dump_modules(self):

        printl.Y("📦 Builtin Modules")

        for name, module in self.modules.items():

            printl.C(
                f"├── {name:<10} → {type(module).__name__}"
            )

        if self.script_modules:

            printl.Y("\n📄 Script Modules")

            for path, module in self.script_modules.items():

                printl.C(
                    f"├── {path.name:<20} → {type(module).__name__}"
                )

    def get_assets_dir(self, create=False):

        path = self.get_assets_dsl_root() / "assets"

        if create:
            path.mkdir(
                parents=True,
                exist_ok=True
            )

        return path

    def get_assets_python_root(self):
        if self.python_root is None:
            raise (
                "Project root chưa được thiết lập"
            )
        return self.python_root
    
    def get_assets_dsl_root(self):

        if self.project_root is None:
            raise RuntimeError(
                "Project root chưa được thiết lập"
            )
        return self.project_root
    
    def get_asset_path(
            self,
            filename,
            create_dir=False
        ):
    
            assets_dir = self.get_assets_dir(
                create=create_dir
            )
    
            return assets_dir / filename

runtime = Runtime()

    