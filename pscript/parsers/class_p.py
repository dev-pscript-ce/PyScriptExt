import sys
sys.dont_write_bytecode = True

from pscript.helpers_ps.wrapper_statement import statement
from ..asts.classes import ClassDef,InstanceObject

class ClassParser:
    @statement("CLASS")
    def parse_class(self):

        self.expect("CLASS")

        name_token = self.expect("IDENT")
        name = name_token.value

        bases = []

        if self.match("LPAREN"):

            while True:

                bases.append(
                    self.parse_expression()
                )

                if not self.match("COMMA"):
                    break

            self.expect("RPAREN")

        body = self.parse_suite()

        return ClassDef(
            name,
            body,
            bases,
            token=name_token,
        )

class Instantiate:
       def instantiate(
        self,
        cls,
        args,
        kwargs
    ):
        obj = InstanceObject(cls)

        try:
            ctor = self.lookup_method(cls,"__init__")
        except NameError:
            ctor = None

        if ctor:
            self.call_function(
                ctor,
                args,
                kwargs,
                self_obj=obj
            )

        return obj