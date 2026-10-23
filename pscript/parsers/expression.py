
import sys
sys.dont_write_bytecode = True

from ..asts.expressions import (
    MemberAccess,
    Variable,
    UnaryExpr,
    IndexExpr,
    BinaryExpr,
    RangeExpression,
    SliceExpr,
    TernaryExpr,
    WalrusExpr,
    UpdateExpr

)

from ..asts.functions import LambdaExpr
from ..asts.statements import Assign
from ..tokens.token_type import TokenType
from ..parameter_kind.paramkind import ParameterKind

class ExpressionParser:
    
    def parse_postfix(self):

        expr = self.parse_primary()

        while True:
            if self.match("DOT"):

                member_token = self.expect("IDENT")

                expr = MemberAccess(
                    expr,
                    member_token.value,
                    token=member_token
                )
                continue

            if self.check("LPAREN"):
                expr = self.finish_paren_call(expr)
                continue

            if (
                self.can_start_expression()
                and isinstance(expr, (Variable, MemberAccess))
            ):
                expr = self.finish_dsl_call(expr)
                
                continue

            if self.match("LBRACKET"):
                expr = self.finish_subscript(expr)
                continue

            if token := self.match("INC", "DEC"):
                expr = UpdateExpr(
                    expr,
                    token.value,
                    prefix=False
                )
                continue

            break

        return expr
    
    def can_start_expression(self):

        return self.check(
            "NUMBER",
            "STRING",
            "BOOL",
            "IDENT",
            "LPAREN"
        )

    def finish_subscript(self, obj):

            start = stop = step = None

            # [ ... ]
            if not self.check("COLON", "RBRACKET"):
                start = self.parse_expression()

            # Không có ':' => index
            if not self.match("COLON"):

                self.expect("RBRACKET")

                return IndexExpr(obj, start)

            # Có ':' => slice

            if not self.check("COLON", "RBRACKET"):
                stop = self.parse_expression()

            if self.match("COLON"):

                if not self.check("RBRACKET"):
                    step = self.parse_expression()

            self.expect("RBRACKET")

            return SliceExpr(
                obj,
                start,
                stop,
                step
            )
    
    def parse_unary(self):

        if token := self.match("PLUS","MINUS","NOT"):

            return UnaryExpr(
                token.value,
                self.parse_unary()
            )
        if token := self.match("INC", "DEC"):

            target = self.parse_postfix()
            return UpdateExpr(
                target,
                token.value,
                prefix=True
            )

        return self.parse_postfix()
    
    
    def parse_factor(self):#( chỉ dùng match)

        left = self.parse_unary()
        
        while token := self.match("STAR", "SLASH", "PERCENT"):
                
                right = self.parse_unary()

                left = BinaryExpr(left, token.value, right)

        return left
    
    def parse_additive(self):#( dùng check + expect)
        
        left = self.parse_factor_bin()
        
        while True:

            if self.check("PLUS", "MINUS"):
                token = self.expect("PLUS", "MINUS")

                right = self.parse_factor_bin()

                left = BinaryExpr(left, token.value, right)
            else:
                break
        return left
    
    def parse_range(self):

        left = self.parse_additive()

        if self.match("RANGE"):

            right = self.parse_additive()

            return RangeExpression(
                left,
                right
            )

        return left
    
    def parse_compare(self):

        left = self.parse_range()

        while token := self.match(
            "LT",
            "GT",
            "LE",
            "GE",
            "IN",
        ):
            right = self.parse_range()

            left = BinaryExpr(
                left,
                token.value, 
                right
            )
        return left

    def parse_equality(self):

        left = self.parse_compare()

        while token := self.match("EQ","NE"):
            right = self.parse_compare()

            left = BinaryExpr(left, token.value, right)

        return left

    def parse_logic_and(self):

        left = self.parse_equality()

        while token := self.match("AND"):

            right = self.parse_equality()

            left = BinaryExpr(
                left,
                token.value,
                right
            )

        return left
    
    def parse_logic_or(self):

        left = self.parse_logic_and()

        while token := self.match("OR"):

            right = self.parse_logic_and()

            left = BinaryExpr(
                left,
                token.value,
                right
            )

        return left

    def is_lambda(self):

        # x => ...
        if (
            self.check("IDENT")
            and self.check("ARROW", offset=1)
        ):
            return True

        # ( ... ) => ...
        if not self.check("LPAREN"):
            return False

        depth = 0

        i = self.pos

        while i < len(self.tokens):

            token = self.tokens[i]

            if token.kind == "LPAREN":
                depth += 1

            elif token.kind == "RPAREN":

                depth -= 1

                if depth == 0:

                    return (
                        i + 1 < len(self.tokens)
                        and self.tokens[i + 1].kind == "ARROW"
                    )

            i += 1

        return False

    def looks_like_lambda(self):

        save = self.pos

        try:

            # =================================
            # x =>
            # =================================

            if (
                self.check("IDENT")
                and self.check(
                    "ARROW",
                    offset=1,
                )
            ):
                return True

            # =================================
            # Phải bắt đầu bằng (
            # =================================

            if not self.check("LPAREN"):
                return False

            self.pos += 1

            # =================================
            # ()
            # =================================

            if self.check("RPAREN"):
                return self.check(
                    "ARROW",
                    offset=1,
                )

            # =================================
            # (...parameters...)
            # =================================

            while True:

                # -----------------------------
                # EOF
                # -----------------------------

                if self.current() is None:
                    return False

                # -----------------------------
                # *
                # -----------------------------

                if self.match("STAR"):

                    # **kwargs

                    if self.match("STAR"):

                        if not self.check("IDENT"):
                            return False

                        self.pos += 1

                    # *args

                    elif self.check("IDENT"):

                        self.pos += 1

                    # bare *
                    #
                    # (a, *, b) =>
                    #

                    else:
                        pass

                    if self.match("COMMA"):
                        continue
                    break

                # -----------------------------
                # Normal parameter
                # -----------------------------

                elif self.check("IDENT"):

                    self.pos += 1

                    # Default
                    # (x = value) =>
                    if self.match("EQUAL"):
                        self.skip_lambda_default()

                # -----------------------------
                # Không phải parameter
                # -----------------------------

                else:

                    return False

                # -----------------------------
                # comma
                # -----------------------------

                if self.match("COMMA"):

                    # trailing comma

                    if self.check("RPAREN"):
                        break

                    continue

                break

            # =================================
            # )
            # =================================

            if not self.match("RPAREN"):
                return False

            # =================================
            # =>
            # =================================

            return self.check("ARROW")

        finally:

            self.pos = save

    def parse_lambda(self):

        if not self.looks_like_lambda():
            return self.parse_logic_or()

        params = []

        #
        # x =>
        #

        if (
            self.check("IDENT")
            and self.check("ARROW", offset=1)
        ):

            params.append(
                self.parse_parameter_list()
            )

        #
        # (...) =>
        #

        else:

            self.expect("LPAREN")

            if not self.check("RPAREN"):

                keyword_only = False

                while True:

                    params.append(
                        self.parse_parameter(
                            keyword_only=keyword_only
                        )
                    )

                    #
                    # bare *
                    #

                    if (
                        params[-1].kind
                        == ParameterKind.KEYWORD_ONLY
                    ):
                        keyword_only = True

                    if not self.match("COMMA"):
                        break

            self.expect("RPAREN")

        self.expect("ARROW")

        if self.check(
            "LBRACE",
            "COLON",
            "INDENT"
        ):
            body = self.parse_suite()
        else:
            body = self.parse_expression()

        return LambdaExpr(params, body)

    def skip_lambda_default(self):

        depth = 0

        while self.current() is not None:

            token = self.current()

            # =================================
            # Nếu đang ở cấp ngoài cùng:
            # gặp , hoặc ) thì dừng
            # =================================

            if depth == 0 and token.kind in (
                "COMMA",
                "RPAREN",
            ):
                return

            # =================================
            # Theo dõi ngoặc lồng nhau
            # =================================

            if token.kind in (
                "LPAREN",
                "LBRACKET",
                "LBRACE",
            ):
                depth += 1

            elif token.kind in (
                "RPAREN",
                "RBRACKET",
                "RBRACE",
            ):

                if depth > 0:
                    depth -= 1

            self.pos += 1
    
    def parse_ternary(self):

        condition = self.parse_lambda()

        if self.match("QUESTION"):
        
            then_expr = self.parse_expression()

            self.expect("COLON")

            else_expr = self.parse_expression()

            return  TernaryExpr(
                condition,
                then_expr,
                else_expr
            )
        return condition


    def parse_assignment(self):

        lhs = self.parse_ternary()

        # =================================
        # Walrus assignment
        #
        # name := value
        # =================================

        if walrus_token := self.match(
            "WALRUS",
        ):

            if not isinstance(
                lhs,
                Variable,
            ):

                self.syntax_error(
                    message=(
                        "Invalid walrus target"
                    ),

                    code=(
                        "PSCRIPT_INVALID_WALRUS_TARGET"
                    ),

                    token=walrus_token,
                )

            rhs = self.parse_assignment()

            return WalrusExpr(
                lhs,
                rhs,
            )

        # =================================
        # Normal assignment
        #
        # name = value
        # obj.value = value
        # items[0] = value
        # =================================

        if assign_token := self.match(
            *TokenType.ASSIGN_OP,
        ):

            if not isinstance(
                lhs,
                (
                    Variable,
                    MemberAccess,
                    IndexExpr,
                ),
            ):

                self.syntax_error(
                    message=(
                        "Invalid assignment target"
                    ),

                    code=(
                        "PSCRIPT_INVALID_ASSIGNMENT_TARGET"
                    ),

                    token=assign_token,
                )
            rhs = self.parse_assignment()


            return Assign(
                lhs,
                assign_token.value,
                rhs,
            )

        return lhs

    def parse_expression(self):

        return self.parse_assignment()
    
    def parse_binary(self, operand_parser, *operators):

        left = operand_parser()

        while token := self.match(*operators):

            right = operand_parser()

            left = BinaryExpr(
                left,
                token.value,
                right,
                token=token,
            )

        return left
    
    def parse_factor_bin(self):

        return self.parse_binary(
            self.parse_unary,"STAR","SLASH", "PERCENT"
        )
# ------------------------------------------------------- #