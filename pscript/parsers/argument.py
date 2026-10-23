import sys
sys.dont_write_bytecode = True

from ..asts.functions import FunctionCall

from ..asts.arguments import (
    NamedArgument,
    StarArgument,
    KwStarArgument
    
)

class Arguments:

    def parse_argument(self):

        # *args
        if self.check("STAR"):

            token = self.expect(
                "STAR"
            )

            return StarArgument(
                self.parse_expression(),
                token=token,
            )

        # **kwargs
        if self.check("DOUBLESTAR"):

            token = self.expect(
                "DOUBLESTAR"
            )

            return KwStarArgument(
                self.parse_expression(),
                token=token,
            )

        # name = value
        if (
            self.check("IDENT")
            and self.check(
                "EQUAL",
                offset=1,
            )
        ):

            name_token = self.expect(
                "IDENT"
            )

            self.expect("EQUAL")

            value = self.parse_expression()

            return NamedArgument(
                name_token.value,
                value,
                token=name_token,
            )

        return self.parse_expression()
    
    
    def parse_argument_list(
        self,
        paren=False,
    ):

        args = []

        # =================================
        # Call nhiều dòng
        # =================================

        if paren:
            self.skip_layout()

        while self.current():

            # =================================
            # Stop
            # =================================

            if paren:

                if self.check(
                    "RPAREN",
                ):
                    break

            else:

                if self.check(
                    "NEWLINE",
                    "RBRACE",
                ):
                    break

            # =================================
            # Parse argument
            # =================================

            start_pos = self.pos

            args.append(
                self.parse_argument()
            )

            # =================================
            # Safety guard
            # =================================

            if self.pos == start_pos:

                self.syntax_error(
                    message=(
                        "Parser made no progress "
                        "while parsing arguments"
                    ),
                    code=(
                        "PSCRIPT_PARSER_STALLED"
                    ),
                )

            # =================================
            # Parenthesized call
            # =================================

            if paren:

                self.skip_layout()

                if self.match(
                    "COMMA",
                ):

                    self.skip_layout()

                    # Cho phép:
                    #
                    # Printl(
                    #     "Hello",
                    # )
                    #

                    if self.check(
                        "RPAREN",
                    ):
                        break

                    continue

                # Không có comma
                # → hết danh sách argument

                break

            # =================================
            # DSL style
            # =================================

            if self.match(
                "COMMA",
            ):
                continue

            if not self.can_start_expression():
                break

        return args
    

    def finish_paren_call(self, callee):

        lparen_token=self.expect("LPAREN")

        args = self.parse_argument_list(
            paren=True
        )

        rparen_token=self.expect("RPAREN")

        return FunctionCall(
            callee,
            args,
            lparen_token=lparen_token,
            rparen_token=rparen_token
        )
    
    def finish_dsl_call(self, callee):

        return FunctionCall(
            callee,
            self.parse_argument_list()
        )