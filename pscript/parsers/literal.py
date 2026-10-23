import sys
sys.dont_write_bytecode = True

from..asts.literals import (
    Number,
    String,
    FString,
    Boolean,
    Null,
    ListLiteral,
    TupleLiteral,
    SetLiteral,
    DictLiteral,
)

from ..asts.expressions import (
    Variable,
    MemberAccess
)

from ..asts.classes import SuperExpr

class LiteralParser:

    def parse_primary(self):

        if self.check("FUNC"):
            return self.parse_anonymous_function()

        if self.check("NUMBER"):
            return self.parse_number()

        if self.check("STRING"):
            return self.parse_string()

        if self.check("BOOL"):
            return self.parse_boolean()

        if self.check("NULL"):
            return self.parse_null()
        
        if self.check("LPAREN"):
            return self.parse_paren()

        if self.check("LBRACKET"):
            return self.parse_list()
        
        if self.check("LBRACE"):
            return self.parse_brace()

        if self.check("IDENT"):
            return self.parse_ident()

        if self.match("SUPER") :
            return SuperExpr()
        
        token = self.current()
        
        if token is None or self.check("EOF"):

            self.syntax_error(
                message="Unexpected EOF",
                code="PSCRIPT_UNEXPECTED_EOF",
                token=token
            )
            return None

        self.syntax_error(
        message=(
        f"Unexpected token "
        f"{token.kind}({token.value})"
        ),

        code="PSCRIPT_UNEXPECTED_TOKEN",

        token=token,

        )
        return None

    def parse_number(self):
        value = self.expect("NUMBER").value
        return Number(
            float(value) if "." in value else int(value)
        )
    
    def parse_string(self):

        value = self.expect("STRING").value

        if "${" in value:
            return self.parse_fstring(value)

        return String(value)
    
    def parse_fstring(self, text):

        parts = []

        i = 0

        while i < len(text):
            start = text.find("${",i)

            if start == -1:
                if i < len(text):
                    parts.append(text[i:])
                break
            if start > i:
                parts.append(text[i:start])
            depth = 1
            j = start + 2

            while j < len(text):
                if text[j] == "{":
                    depth += 1
                elif text[j] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            if depth != 0:

                self.syntax_error(
                    message="Unterminated ${}",
                    code=(
                        "PSCRIPT_UNTERMINATED_INTERPOLATION"
                    ),
                )

            expr_source = text[start+2:j]

            parts.append(
                self.parse_embedded_expression(expr_source)
            )

            i = j + 1

        return FString(parts)

    def parse_boolean(self):
        return Boolean(self.expect("BOOL").value == "true")
    
    def parse_null(self):
        self.expect("NULL")
        return Null()
    
    def parse_list(self):
        self.expect("LBRACKET")
        elements = []

        self.skip_layout()

        if not self.check("RBRACKET"):

            while True:
                elements.append(
                    self.parse_expression()
                )
                self.skip_layout()

                if self.match("COMMA"):

                    self.skip_layout()

                    continue
                break
        self.expect("RBRACKET")


        return ListLiteral(elements)

    def parse_ident(self):
        
        token = self.expect("IDENT")

        node = Variable(token.value,token=token)

        while self.match("DOT"):

            member_token = self.expect("IDENT")
            
            node = MemberAccess(node, member_token.value,token=member_token)
        return node



    # -------------------------------------------------------

    def parse_paren(self):

        self.expect("LPAREN")

        self.skip_layout()

        # ()
        if self.match("RPAREN"):
            return TupleLiteral([])

        first = self.parse_expression()

        self.skip_layout()

        # (expr)
        if not self.match("COMMA"):

            self.skip_layout()

            self.expect("RPAREN")

            return first

        # (expr, ...)
        elements = [first]

        while True:

            self.skip_layout()

            # (expr,)
            if self.check("RPAREN"):
                break

            elements.append(
                self.parse_expression()
            )

            self.skip_layout()

            if not self.match("COMMA"):
                break

        self.skip_layout()

        self.expect("RPAREN")

        return TupleLiteral(elements)

    def parse_brace(self):

        self.expect("LBRACE")

        self.skip_layout()

        #
        # {}
        #
        if self.match("RBRACE"):
            return DictLiteral([])

        #
        # Xem phần tử đầu tiên
        #
        save = self.pos

        try:

            if self.match("STRING"):
            
                self.skip_layout()

                is_dict = self.match("COLON")

            elif self.check("IDENT"):
                
                self.skip_layout()

                is_dict = self.match("COLON")

            else:
                is_dict = False

        finally:
            self.pos = save

        if is_dict:
            return self.finish_dict()

        return self.finish_set()
    
    def finish_dict(self):

        items = []

        self.skip_layout()

        while not self.check("RBRACE"):

            #
            # key
            #

            if self.check("STRING"):

                key = self.parse_string()

            elif self.check("IDENT"):

                key = self.parse_ident()

            else:

                token = self.current()

                self.syntax_error(
                    message=(
                        "Expected dictionary key, "
                        f"got {token}"
                    ),
                    code=(
                        "PSCRIPT_INVALID_DICTIONARY_KEY"
                    ),
                    token=token,
                )

            self.skip_layout()

            self.expect("COLON")

            self.skip_layout()

            value = self.parse_expression()

            items.append(
                (
                    key,
                    value,
                )
            )

            self.skip_layout()

            if self.match("COMMA"):

                self.skip_layout()

                continue

            break

        self.skip_layout()

        self.expect("RBRACE")

        return DictLiteral(
            items,
        )
    
    def finish_set(self):

        values = []

        self.skip_layout()

        while not self.check("RBRACE"):

            values.append(
                self.parse_expression()
            )

            self.skip_layout()

            if self.match("COMMA"):
                self.skip_layout()
                continue

            break

        self.skip_layout()

        self.expect("RBRACE")

        return SetLiteral(values)