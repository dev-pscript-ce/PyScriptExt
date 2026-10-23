import sys
sys.dont_write_bytecode=True

from pscript.parameter_kind.paramkind import(
    ParameterKind
)

def function_to_method(function):

        parameters = []

        for parameter in function.params:

            parameters.append({
                "name": parameter.name,
                "required": parameter.default is None,
                "variadic": (
                    parameter.kind
                    == ParameterKind.VAR_POSITIONAL
                ),
                "varkwargs": (
                    parameter.kind
                    == ParameterKind.VAR_KEYWORD
                ),
            })

        return {
            "name": function.name,
            "parameters": parameters,
        }

def get_node_position(node):

        token = getattr(
            node,
            "token",
            None,
        )

        if token is None:
            return 1, 1, 1

        line = max(
            getattr(token, "line", 1),
            1,
        )

        column = max(
            getattr(token, "column", 1),
            1,
        )

        length = getattr(
            token,
            "length",
            None,
        )

        if length is None:

            value = getattr(
                token,
                "value",
                "",
            )

            length = max(
                len(str(value or "")),
                1,
            )

        return (
            line,
            column,
            max(length, 1),
        )

