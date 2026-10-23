import sys
sys.dont_write_bytecode = True

from pscript.tokens.token import Token

from pscript.errors.pscript_errors import PscriptSyntaxError

OPERATORS={

        ".." : "RANGE",

        "==" : "EQ",

        "!=" : "NE",
        
        "!" : "NOT",

        "<=" : "LE",

        ">=" : "GE",

        "&&" : "AND",

        "||" : "OR",
        
        "++" : "INC",

        "--" : "DEC",

        "+=" : "PLUS_EQUAL",

        "-=" : "MINUS_EQUAL",

        "*=" : "STAR_EQUAL",

        "/=" : "SLASH_EQUAL",

        "%=" : "MOD_EQUAL",
        
        ":=" : "WALRUS",

        "=>" : "ARROW",

        "=" : "EQUAL",

        "<" : "LT",
 
        ">" : "GT",

        "+" : "PLUS",

        "-" : "MINUS",

        "*" : "STAR",

        "/" : "SLASH",
        
        "**" : "DOUBLESTAR",

        "(" : "LPAREN",

        ")" : "RPAREN",

        "{" : "LBRACE",

        "}" : "RBRACE",

        "[" : "LBRACKET",

        "]" : "RBRACKET",
        
        "?" : "QUESTION",
        
        "%" : "PERCENT",

        ":" : "COLON",

        "," : "COMMA",

        "." : "DOT",

    }


KEYWORDS = {
    "true": "BOOL",
    "false": "BOOL",
    "null": "NULL",
    "" : "EOF",

    "if" : "IF",
    "elif" : "ELIF",
    "else" : "ELSE",
    "while" : "WHILE",
    "for" : "FOR",
    "in" : "IN",
    "func" : "FUNC",
    "return" : "RETURN",
    "break" : "BREAK",
    "continue" : "CONTINUE",
    "import" : "IMPORT",
    "from" : "FROM",
    "as" : "AS",
    "class" : "CLASS",
    "super" : "SUPER",
    "switch": "SWITCH",
    "case": "CASE",
    "default": "DEFAULT",
    "try": "TRY",
    "catch": "CATCH",
    "finally": "FINALLY",
}

class Scanner:

    def __init__(self, text):

        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1

        self.indents = [0] # thêm indents
        self.at_line_start = True

        self.tokens = []

        # self.SPECIAL_IDENTIFIERS = {
        #     "Hot-Key",
        #     "Set-Interval",
        #     "Click-Img",
        #     "Wait-Text",
        #     "Double-Click",
        #     "Move-Rel",
        #     "Find-Text" ,
            
        # } # => [off] hỗ trợ "-" <=> Hot-Key

    def scan(self):

        while not self.eof():

            # Chỉ xử lý indent khi đang ở đầu dòng
            if self.at_line_start :

                self.process_indentaion()
                self.at_line_start = False

                if self.eof(): break

            ch = self.current()

            if ch.isspace() and ch != "\n":
                self.skip_whitespace()

            elif ch == "\n":
                self.scan_newline()

            elif ch.isdigit():
                self.scan_number()

            elif ch in "\"'":
                self.scan_string()

            elif ch.isalpha() or ch in "_$":
                self.scan_identifier()
            
            elif ch == "/":
                self.scan_slash()

            elif ch == "#":
                self.scan_hash_comment()

            else: self.scan_operator()

        # EOF còn dư indent thì emit DEDENT
        while len(self.indents) > 1:
            self.indents.pop()
            self.emit("DEDENT")
            
        # for t in self.tokens:
        #     # print(t.kind, repr(t.value))        
        
        return self.tokens

    def scan_hash_comment(self):

        self.advance()      # bỏ '#'

        while not self.eof() and self.current() != "\n":
            self.advance()
    
    def eof(self):
        return self.pos >= len(self.text)
    
    def current(self):
        if self.eof():
            return "\0"
        return self.text[self.pos]
    
    def peek (self, offset=1):
        pos = self.pos + offset

        if pos>= len(self.text):
            return "\0"
        return self.text[pos]
    
    def advance(self):

        ch = self.current()

        self.pos += 1

        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return ch
    
    def emit(self, kind, value=None, line=None, column=None):

        self.tokens.append(
            Token(
                kind,
                value,
                line if line is not None else self.line,
                column if column is not None else self.column
            )
        )

    def skip_whitespace(self):

        while self.current() in " \t\r":

            self.advance()

    def scan_newline(self):

        while self.current() == "\n":
            self.advance()
            self.emit("NEWLINE")

        self.at_line_start = True


    def scan_special_identifier(self, name):
        save = (
                self.pos,
                self.line,
                self.column
            )

        while True:
            

            if self.current() != "-":
                break

            self.advance()

            start = self.pos

            while (
                not self.eof()
                and (
                    self.current().isalnum()
                    or self.current() in "_$"
                )
            ):
                self.advance()

            second = self.text[start:self.pos]

            candidate = f"{name}-{second}"

            if candidate in self.SPECIAL_IDENTIFIERS:
                name = candidate

            else:
                self.pos, self.line, self.column = save
                break

        return name
    
    def scan_ident(self):
        start = self.pos

        while (
            not self.eof()
            and (
                self.current().isalnum()
                or self.current() in "_$" 
            )
        ):
            self.advance()

        name = self.text[start:self.pos]

        return name
    
    def scan_indent(self):

        indent = 0

        while not self.eof():

            ch = self.current()

            if ch == " ":
                indent += 1
                self.advance()

            elif ch == "\t":
                indent += 4
                self.advance()

            else:
                break

        return indent
    
    def process_indentaion(self):

        if self.eof():
            return

        indent = self.scan_indent()

        if self.eof():
            return

        if self.current() == "\n":
            return

        current = self.indents[-1]

        if indent > current:
            self.indents.append(indent)
            self.emit("INDENT")

        elif indent < current:

            while indent < self.indents[-1]:
                self.indents.pop()
                self.emit("DEDENT")

            if indent != self.indents[-1]:
                raise PscriptSyntaxError(
                    message="Invalid indentation",
                    line= self.line,
                    column=1,
                    code="PSCRIPT_INVALID_INDENTATION"
                )

    
    def scan_identifier(self):

        # Lưu vị trí trước khi đọc IDENT
        start_line = self.line

        start_column = self.column

        name = self.scan_ident()

        self.emit(
            KEYWORDS.get(
                name,
                "IDENT",
            ),
            name,
            line=start_line,
            column=start_column,
        )

    def scan_number(self):

        # Lưu vị trí trước khi đọc NUMBER
        start_line = self.line

        start_column = self.column

        start = self.pos

        while (
            not self.eof()
            and self.current().isdigit()
        ):

            self.advance()

        if (
            not self.eof()
            and self.current() == "."
            and self.peek().isdigit()
        ):

            self.advance()

            while (
                not self.eof()
                and self.current().isdigit()
            ):

                self.advance()

        self.emit(
            "NUMBER",
            self.text[
                start:self.pos
            ],
            line=start_line,
            column=start_column,
        )

    def scan_string(self):

        quote = self.current()

        # """ hoặc '''
        if (
            self.peek() == quote and
            self.peek(2) == quote
        ):
            return self.scan_multiline_string()

        return self.scan_single_string()

    def scan_single_string(self):

        quote = self.current()      # ' hoặc "

        start_line = self.line
        start_column = self.column

        self.advance()              # bỏ dấu mở

        value = []

        while not self.eof():

            ch = self.current()

            if ch == "\\":
                self.advance()

                
                if self.eof():

                    raise PscriptSyntaxError(
                        message=(
                            "Unterminated escape sequence"
                        ),

                        line=self.line,

                        column=self.column,

                        code=(
                            "PSCRIPT_UNTERMINATED_ESCAPE"
                        ),
                    )


                esc = self.current()

                escapes = {
                    "n": "\n",
                    "t": "\t",
                    "r": "\r",
                    '"': '"',
                    "'": "'",
                    "\\": "\\",
                }

                value.append(
                    escapes.get(esc, esc)
                )

                self.advance()

                continue

            if ch == quote:

                self.advance()

                self.emit(
                    "STRING",
                    "".join(value),
                    line=start_line,
                    column=start_column,
                )

                return

            value.append(ch)

            self.advance()

        raise PscriptSyntaxError(
            message="Unterminated string",
            line=start_line,
            column=start_column,
            code="PSCRIPT_UNTERMINATED_STRING"
        )

    def scan_multiline_string(self):

        quote = self.current()

        start_line = self.line

        start_column = self.column

        # bỏ """
        self.advance()
        self.advance()
        self.advance()

        value = []

        while not self.eof():

            if (
                self.current() == quote
                and self.peek() == quote
                and self.peek(2) == quote
            ):

                self.advance()
                self.advance()
                self.advance()

                self.emit(
                    "STRING",
                    "".join(value),
                    line=start_line,
                    column=start_column,
                )

                return

            value.append(
                self.current()
            )

            self.advance()

        raise PscriptSyntaxError(
            message="Unterminated multiline string",
            line=start_line,
            column = start_column,
            length=3,
            code="PSCRIPT_UNTERNATE_MULTILINE_STRINH"

        )

    def scan_slash(self):

        # //
        if self.peek() == "/":

            self.advance()
            self.advance()

            while self.current() != "\n" and not self.eof():
                self.advance()

            return
        if self.peek() == "#":

            self.advance()

            while self.current() != "\n" and not self.eof():
                self.advance()

            return

        # /*
        if self.peek() == "*":

            start_line = self.line
            start_colunm = self.column

            self.advance()
            self.advance()

            depth = 1

            while depth > 0:

                if self.eof():
                    raise PscriptSyntaxError(
                        message="Unterminal comment",
                        line=start_line,
                        column=start_colunm,
                        length=2,
                        code="Pscript_UNTERMINAL_COMMEN"
                    )

                if self.current() == "/" and self.peek() == "*":
                    depth += 1
                    self.advance()
                    self.advance()
                    continue

                if self.current() == "*" and self.peek() == "/":
                    depth -= 1
                    self.advance()
                    self.advance()
                    continue

                self.advance()

            return

        self.scan_operator()

    def scan_escape(self):

        self.advance()      # bỏ \

        ch = self.current()

        mapping = {
            "n": "\n",
            "t": "\t",
            "r": "\r",
            "\\": "\\",
            '"': '"',
            "'": "'",
        }

        self.advance()

        return mapping.get(ch, ch)

    def scan_operator(self):

        next_char = self.peek() or ""

        two = self.current()+next_char

        if two in OPERATORS:

            self.emit(
                OPERATORS[two],
                two
            )

            self.advance()
            self.advance()

            return

        one = self.current()

        if one in OPERATORS:

            self.emit(
                OPERATORS[one],
                one
            )

            self.advance()

            return

        raise PscriptSyntaxError(
            message=f"Unknown charater {repr(one)}",
            line=self.line,
            column=self.column,
            length=1,
            code="PSCRIPT_UNKNOWN_CHARATER"
        )
    
    