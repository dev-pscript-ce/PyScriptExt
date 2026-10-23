import sys
sys.dont_write_bytecode = True

from ..helpers_ps.wrapper_statement import statement
from ..asts.functions import (
    FunctionDef,
    AnonymousFunction
)

class DeclarationParser:
    
    @statement("FUNC")
    def parse_function(self):

        self.expect(
            "FUNC"
        )

        name_token = self.expect(
            "IDENT"
        )

        if self.check("LPAREN"):

            params = (
                self.parse_parameter_list()
            )

        else:

            params = []

        body = self.parse_suite()

        return FunctionDef(
            name=name_token.value,
            params=params,
            body=body,
            token=name_token,
        )
    
class AnonymousParse:

    def parse_anonymous_function(self):

        self.expect("FUNC")

        params = self.parse_parameter_list()

        body = self.parse_suite()

        return AnonymousFunction(
            params,
            body
        )