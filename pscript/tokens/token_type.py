import sys
sys.dont_write_bytecode = True

class TokenType:

    COMMENT = "COMMENT" # #,//,/* */
    NEWLINE = "NEWLINE" #/n
    SKIP = "SKIP" # /t

    NUMBER = "NUMBER"
    STRING = "STRING"
    
    IDENT = "IDENT"
    INDENT = "INDENT"
    DEDENT = "DEDENT"

    LBRACE = "LBRACE" # {
    RBRACE = "RBRACE" # }
    LPAREN = "LPAREN" # (
    RPAREN = "RPAREN" # )
    LBRACKET = "LBRACKET" # [
    RBRACKET = "RBRACKET" # ]

    QUESTION = "QUESTION" # ?
    COLON="COLON" # :

    PLUS = "PLUS" # +
    MINUS = "MINUS" # -
    STAR = "STAR" # * # /
    DOUBLESTAR = "DOUBLESTAR"
    SLASH = "SLASH" # /
    PERCENT = "PERCENT" # %
    EQ = "EQ" # ==
    NE = "NE" # !=
    LE = "LE" # <=
    GE = "GE" # >=
    WALRUS = "WALRUS" # :=
    ARROW = "ARROW" # =>
    AND = "AND" # &&
    OR = "OR" # ||
    NOT = "NOT" # !
    LT = "LT" # <
    GT = "GT" # >
    COMMA = "COMMA" # ,
    RANGE = "RANGE" # ..
    DOT = "DOT" # .

    ASSIGN_OP = (
        "PLUS_EQUAL",
        "MINUS_EQUAL",
        "STAR_EQUAL",
        "SLASH_EQUAL",
        "MOD_EQUAL",
        "EQUAL",
    )

    # ====== KEYWORDS ====== #
    BOOL = "BOOL" # true | false
    NULL = "NULL" # null
    EOF = "EOF"

    IF = "IF"
    ELIF = "ELIF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    FOR = "FOR"
    IN = "IN"
    FUNC = "FUNC"
    RETURN = "RETURN"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    IMPORT = "IMPORT"
    FROM = "FROM"
    AS = "AS"
    CLASS = "CLASS"
    SUPER = "SUPER"
    SWITCH = "SWITCH"
    CASE = "CASE"
    DEFAULT = "DEFAULT"
    TRY = "TRY"
    CATCH = "CATCH"
    FINANLLY = "FINALLY"







    