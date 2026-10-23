import sys
sys.dont_write_bytecode = True

from pscript.helpers.color import printl

class DebugStyle:

    STYLES = {
        # Runtime:
        "call": {
            "icon": "📞",
            "color": printl.C,
        },
        "return":{
            "icon": "↩",
            "color": printl.G,
        },

        # Symbol Table:
        "define": {
            "icon": "📦",
            "color": printl.B,
        },
        "lookup": {
            "icon": "🔍",
            "color": printl.M,
        },
        "assign": {
            "icon": "📝",
            "color": printl.Y,
            "group": "symbol"
        },
        "scope": {
            "icon": "📂",
            "color": printl.B,
        },

        # Execution Trace:
        "loop": {
            "icon": "🔁",
            "color": printl.G,
        },


        "branch": {
            "icon":"❓",
            "color":printl.Y,
        },

        # Object:
        "member": {
            "icon": "📦",
            "color": printl.M,
        },
    }

    GROUPS = {

        "scanner": {
            "token",
            "lexer",
        },

        "parser": {
            "ast",
            "parse",
            "expr",
            "stmt",
        },

        "runtime": {
            "call",
            "return",

        },

        "symbol": {
            "define",
            "lookup",
            "assign",
            "scope",
        },

        "trace": {
            "loop",
            "branch",
            "break",
            "continue",
        },

        "object":{
            "member",
            "index",
            "attribute"
        },

        "all": {
            "*"
        }
    }

    @classmethod
    def render(cls, depth, category, *args):

        style = cls.STYLES[category]

        prefix = "│   " * depth + "├── "

        style["color"](
            prefix,
            style["icon"],
            *args
        )