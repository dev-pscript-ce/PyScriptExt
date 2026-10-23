import sys
sys.dont_write_bytecode = True
from .base import StatementNode

# class Import(StatementNode):

#     def __init__(
#         self,
#         module: str,
#         alias: str | None = None,
#         is_file: bool = False,
#         token=None,
#     ):
#         super().__init__(token)

#         self.module = module
#         self.alias = alias
#         self.is_file = is_file

class Import(StatementNode):

    def __init__(
        self,
        imports,
        token=None,
    ):
        super().__init__(token)

        # [
        #     (module, alias, is_file),
        #     ...
        # ]
        self.imports = imports

        # -----------------------------------------
        # Backward compatibility
        # -----------------------------------------

        if len(imports) == 1:

            (
                self.module,
                self.alias,
                self.is_file,
            ) = imports[0]

        else:

            self.module = None
            self.alias = None
            self.is_file = False



class FromImport(StatementNode):
    def __init__(self, module:str, names:list[tuple[str|None]],token=None):
        super().__init__(token)
        self.module = module
        self.names = names

    def __repr__(self):
        return (
            f"FromImport("
            f"{self.module},"
            f"{self.names}"
        )
