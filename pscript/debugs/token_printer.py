import sys
sys.dont_write_bytecode = True

from pscript.helpers.color import printl

class TokenPrinter:

    COLORS = {

        "IDENT":"Y",

        "NUMBER":"C",

        "STRING":"G",

        "BOOL":"G",

        "NULL":"M",

        "FOR":"B",
        "IF":"B",
        "WHILE":"B",
        "RETURN":"B",
    }

    def color(self,kind):
        return self.COLORS.get(kind,"W")

    def print(self, tokens):

        if not tokens:
            printl.Y("No tokens")
            return

        rows = []

        for tok in tokens:

            rows.append({
                "TYPE": tok.kind,
                "VALUE": repr(tok.value)[1:-1],
                "LINE": tok.line,
                "COL": tok.column,
            })

        printl.C("TOKEN STREAM")
        printl.table(rows)