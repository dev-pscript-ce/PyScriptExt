import sys
sys.dont_write_bytecode=True

from pscript.asts.expressions import Variable
from pscript.asts.functions import FunctionDef
from pscript.analyzers.core.definitions import BUILTINS
from pscript.analyzers.core.utils import function_to_method

class ValidateFunctionCall:

    def validate_FunctionCall(
        self,
        call,
    ):

        callee = call.callee

        if not isinstance(
            callee,
            Variable,
        ):
            return

        function_name = callee.name

        # =================================
        # Built-in
        # =================================

        builtin_methods = BUILTINS.get(
            "methods",
            {}
        )

        method = builtin_methods.get(
            function_name
        )

        if method is not None:

            self.validate_arguments(
                call=call,
                method=method,
                function_name=function_name,
            )

            return

        symbol = self.resolve_symbol(
            function_name
        )

        
        # =================================
        # Built-in callable object
        # =================================

        builtin_object = (
            BUILTINS
            .get("objects", {})
            .get(function_name)
        )

        if (
            isinstance(builtin_object, dict)
            and builtin_object.get("callable", False)
        ):
            self.validate_arguments(
                call=call,
                method=builtin_object,
                function_name=function_name,
            )
            return


        if symbol is None:

            self.add_error(
                node=callee,

                message=(
                    f'Function "{function_name}" '
                    f'is not define:'
                ),

                code=(
                    "PSCRIPT_UNKNOWN_FUNCTION"
                ),
            )

            return

        # =================================
        # Imported function
        # =================================

        if symbol.kind == "import":

            method = symbol.data

            if method is not None:

                self.validate_arguments(
                    call=call,
                    method=method,
                    function_name=function_name,
                )

            return

        # =================================
        # User-defined function
        # =================================

        if symbol.kind == "user_defined_function":

            function = symbol.node

            if not isinstance(
                function,
                FunctionDef,
            ):
                return

            method = function_to_method(
                function
            )

            self.validate_arguments(
                call=call,
                method=method,
                function_name=function_name,
            )

            return
