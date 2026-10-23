import sys
sys.dont_write_bytecode = True

from.utils import get_node_position

class DiagnosticError:

    def add_error(
        self,
        node=None,
        message="",
        code="PSCRIPT_ANALYSIS_ERROR",
        severity="error",
        token=None,
        length=None,
        line=None,
        column=None,
    ):

        if token is not None:

            line = max(getattr(token, "line", 1), 1)
            column = max(getattr(token, "column", 1), 1)

            token_length = getattr(token, "length", None)

            if length is None:
                if token_length is not None:
                    length = token_length
                else:
                    value = getattr(token, "value", "")
                    length = max(len(str(value or "")), 1)

            length = max(length, 1)

        elif line is not None or column is not None:

            line = max(line or 1, 1)
            column = max(column or 1, 1)
            length = max(length or 1, 1)

        else:

            line, column, length = get_node_position(node)

            if length is not None:
                length = max(length, 1)


        # traceback.print_exc()
        self.diagnostics.append(

            create_diagnostic(

                line=line,

                column=column,

                length=length,

                message=message,

                severity=severity,

                code=code,

            )

        )

def create_diagnostic(
    line,
    column,
    length,
    message,
    severity="error",
    code="PSCRIPT_ERROR",
):
    return {
        "line": max(
            line - 1,
            0,
        ),

        "column": max(
            column-1,
            0,
        ),

        "length": max(
            length,
            1,
        ),

        "message": message,

        "severity": severity,

        "code": code,

        "source": "Pscript",
    }
