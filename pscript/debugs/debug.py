import sys
sys.dont_write_bytecode = True

from .style import DebugStyle

class Debug:

    def __init__(self):

        self.flags = set()

        self.depth = 0

    def enable(self, *flags):

        self.flags.update(flags)

    def disable(self, *flags):

        for f in flags:
            self.flags.discard(f)

    def clear(self):

        self.flags.clear()

    def enable_group(self, *groups):

        for group in groups:

            cats = DebugStyle.GROUPS.get(group)

            if cats is None:
                raise ValueError(
                    f"Unknown debug group '{group}'"
                )

            if "*" in cats:
                self.flags.add("*")
            else:
                self.flags.update(cats)

    def log(self, category, *args):

        if category not in self.flags:
            return

        DebugStyle.render(
            self.depth,
            category,
            *args
        )

    def enter(self, category, *args):

        self.log(category, *args)

        self.depth += 1

    def leave(self):

        if self.depth:

            self.depth -= 1  

debug = Debug()

class Debug_:
    
    enabled = True

    @classmethod
    def log(cls, *args, **kwargs):

        if cls.enabled:
            print(*args, **kwargs)

    @classmethod
    def modules(cls, runtime):

        if not cls.enabled:
            return

        print("📦 Runtime Modules")

        items = list(runtime.modules.items())

        for i,(name,module) in enumerate(items):

            prefix = "└──" if i == len(items)-1 else "├──"

            print(
                f"{prefix} {name:<8} → {type(module).__name__}"
            )

    @classmethod
    def scope(cls, scope):

        if not cls.enabled:
            return

        print("📂 Scope")

        items = list(scope.values.items())

        for i,(name,value) in enumerate(items):

            prefix = "└──" if i == len(items)-1 else "├──"

            print(
                f"{prefix} {name:<10} = {value}"
            )

    @classmethod
    def call(cls, name, args):

        if not cls.enabled:
            return

        print(
            f"📞 {name}({', '.join(map(str,args))})"
        )

    @classmethod
    def assign(cls, name, value):

        if not cls.enabled:
            return

        print(
            f"📝 {name} = {value}"
        )

    @classmethod
    def member(cls, obj, member):

        if not cls.enabled:
            return

        print(
            f"📦 {obj}.{member}"
        )

    @classmethod
    def import_module(cls, module, alias):

        if not cls.enabled:
            return

        if alias:
            print(
                f"📥 import {module} as {alias}"
            )
        else:
            print(
                f"📥 import {module}"
            )   

debug_ = Debug_()


