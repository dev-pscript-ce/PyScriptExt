import sys
sys.dont_write_bytecode = True

from ..asts.statements import (
    Block,
    IfStatement,
    WhileStatement,
    ForStatement,
    BreakStatement,
    ContinueStatement,
    ReturnStatement,
    ExpressionStatement,
    CaseClause,
    SwitchStatement,
    CatchClause,
    TryStatement,

)
from ..asts.expressions import Variable
from ..helpers_ps.wrapper_statement import STATEMENTS,statement
from ..tokens.token_type import TokenType

class StatementParser:
    
    def parse_statement(self):
        
        token = self.current()

        if token is None:
            return None
        
        if self.check("LBRACE"):
            return self.parse_lbrace_block()

        parser = STATEMENTS.get(token.kind)

        if parser:
            return parser(self)
        
        expr = self.parse_expression()

        return ExpressionStatement(expr)

    def parse_suite(self):

        self.skip_newlines()

        # -----------------------------
        # { ... }
        # -----------------------------

        if self.check("LBRACE"):
            return self.parse_lbrace_block()

        # -----------------------------
        # : ...
        # -----------------------------

        if self.check("COLON"):
            return self.parse_colon_block()

        # -----------------------------
        # Thiếu : hoặc {
        # -----------------------------

        token = self.current()

        self.syntax_error(
            message=(
                "Expected ':' or '{' "
                "to start block"
            ),
            code=(
                "PSCRIPT_EXPECTED_BLOCK"
            ),
            token=token,
        )
       
    def parse_indent_block(self):

        self.expect(
            "INDENT"
        )

        body = []

        while True:

            self.skip_newlines()

            if self.check(
                "DEDENT"
            ):
                break

            token = self.current()

            if token is None:

                self.syntax_error(
                    message="Missing DEDENT",
                    code=(
                        "PSCRIPT_MISSING_DEDENT"
                    ),
                    token=token,
                )

            body.append(
                self.parse_statement()
            )

        self.expect(
            "DEDENT"
        )

        return Block(
            body
        )
    
    def parse_colon_block(self):

        self.expect("COLON")

        self.skip_newlines() # | self.expect("NEWLINE") -> không cho phép dòng trống 

        return self.parse_indent_block()

    def parse_lbrace_block(self):

        self.expect(
            "LBRACE"
        )

        self.skip_newlines()

        has_indent = self.match(
            "INDENT"
        )

        body = []

        while True:

            self.skip_newlines()

            # Hết block

            if self.check(
                "RBRACE"
            ):
                break

            # Trường hợp lexer emit
            # DEDENT trước }

            if (
                has_indent
                and self.check(
                    "DEDENT"
                )
            ):

                self.expect(
                    "DEDENT"
                )

                self.skip_newlines()

                break

            token = self.current()
            
            if token is None:

                self.syntax_error(
                    message="Missing '}'",
                    code=(
                        "PSCRIPT_MISSING_RBRACE"
                    ),
                    token=token
                )

            body.append(
                self.parse_statement()
            )

            self.skip_newlines()

        self.expect(
            "RBRACE"
        )

        return Block(
            body
        )
    
    def parse_single_statement(self):

        return Block([
            self.parse_statement()
        ])  

    @statement("IF")
    def parse_if(self):

        self.expect("IF")

        condition = self.parse_expression()

        then_block = self.parse_suite()

        elif_blocks = []

        self.skip_newlines()

        while self.check("ELIF"):
            self.expect("ELIF")

            cond = self.parse_expression()
            block = self.parse_suite()

            elif_blocks.append((cond,block))

            self.skip_newlines()

        else_block = None

        if self.match("ELSE"):

            else_block = self.parse_suite()

        return IfStatement(
            condition,
            then_block,
            elif_blocks,
            else_block
        )
    
    @statement("WHILE")
    def parse_while(self):
        self.expect("WHILE")

        condition = self.parse_expression()

        block = self.parse_suite()

        return WhileStatement(condition, block)
    
    @statement("FOR")
    def parse_for(self):

        self.expect("FOR")

        name = self.expect("IDENT").value

        self.expect("IN")

        iterable = self.parse_expression()

        block = self.parse_suite()

        return ForStatement(
            name,
            iterable,
            block
        )
    
    @statement("BREAK")
    def parse_break(self):
        self.expect("BREAK")
        return BreakStatement()
    
    @statement("CONTINUE")
    def parse_continue(self):
        self.expect("CONTINUE")
        return ContinueStatement()
    
    @statement("RETURN")
    def parse_return(self):

        return_token = self.expect("RETURN")

        value = None

        if not self.check(TokenType.NEWLINE,TokenType.RBRACE,TokenType.EOF):
            value = self.parse_expression()

        return ReturnStatement(value,token=return_token)

    @statement("SWITCH")
    def parse_switch(self):

        self.expect("SWITCH")

        expr = self.parse_expression()

        # ---------------------------------
        # switch body
        # ---------------------------------

        if self.match("COLON"):

            self.skip_newlines()

            # switch x:
            #     case ...
            self.expect("INDENT")

            cases = []
            default_block = None

            while True:

                self.skip_newlines()

                if self.check("DEDENT"):
                    break

                if self.match("CASE"):

                    values = [
                        self.parse_expression()
                    ]

                    while self.match("COMMA"):
                        values.append(
                            self.parse_expression()
                        )

                    block = self.parse_suite()

                    cases.append(
                        CaseClause(values, block)
                    )

                    continue

                if self.match("DEFAULT"):

                    if default_block is not None:
                        self.syntax_error(
                            message="Duplicate default clause",
                            code="PSCRIPT_DUPLICATE_DEFAULT",
                            token=self.current(),
                        )

                    default_block = self.parse_suite()

                    continue

                token = self.current()

                self.syntax_error(
                    message="Expected 'case' or 'default' inside switch",
                    code="PSCRIPT_EXPECTED_CASE",
                    token=token,
                )

            self.expect("DEDENT")

            return SwitchStatement(
                expr,
                cases,
                default_block
            )

        # ---------------------------------
        # switch x { ... }
        # ---------------------------------

        if self.check("LBRACE"):

            return self.parse_switch_brace_body(
                expr
            )

        # ---------------------------------
        # invalid
        # ---------------------------------

        token = self.current()

        self.syntax_error(
            message="Expected ':' or '{' after switch expression",
            code="PSCRIPT_EXPECTED_SWITCH_BLOCK",
            token=token,
        )

    def parse_switch_brace_body(self, expr):

        self.expect("LBRACE")

        self.skip_newlines()

        has_indent = self.match("INDENT")

        cases = []
        default_block = None

        while True:

            self.skip_newlines()

            if self.check("RBRACE"):
                break

            # Lexer có thể emit DEDENT trước }
            if (
                has_indent
                and self.check("DEDENT")
            ):
                self.expect("DEDENT")

                self.skip_newlines()

                if self.check("RBRACE"):
                    break

            # ---------------------------------
            # CASE
            # ---------------------------------

            if self.match("CASE"):

                values = [
                    self.parse_expression()
                ]

                while self.match("COMMA"):
                    values.append(
                        self.parse_expression()
                    )

                block = self.parse_suite()

                cases.append(
                    CaseClause(
                        values,
                        block
                    )
                )

                continue

            # ---------------------------------
            # DEFAULT
            # ---------------------------------

            if self.match("DEFAULT"):

                if default_block is not None:
                    self.syntax_error(
                        message="Duplicate default clause",
                        code="PSCRIPT_DUPLICATE_DEFAULT",
                        token=self.current(),
                    )

                default_block = self.parse_suite()

                continue

            # ---------------------------------
            # INVALID
            # ---------------------------------

            token = self.current()

            self.syntax_error(
                message="Expected 'case' or 'default' inside switch",
                code="PSCRIPT_EXPECTED_CASE",
                token=token,
            )

        self.expect("RBRACE")

        return SwitchStatement(
            expr,
            cases,
            default_block
        )

    @statement("TRY")
    def parse_try(self):

        self.expect("TRY")

        try_block = self.parse_suite()

        catches = []

        self.skip_newlines()

        # =================================
        # catch
        # =================================

        while self.match("CATCH"):

            exception_type = None
            name = None

            # ---------------------------------
            # catch:
            # ---------------------------------

            if self.check("COLON"):

                pass

            # ---------------------------------
            # catch IDENT ...
            # ---------------------------------

            elif self.check("IDENT"):

                first_name = self.expect(
                    "IDENT"
                ).value

                # ---------------------------------
                # catch ExceptionType e:
                # ---------------------------------

                if self.check("IDENT"):

                    exception_type = Variable(
                        first_name
                    )

                    name = self.expect(
                        "IDENT"
                    ).value

                # ---------------------------------
                # catch e:
                # ---------------------------------

                else:

                    name = first_name

            else:

                self.syntax_error(
                    message=(
                        "Expected exception type, "
                        "exception name, or ':' "
                        "after 'catch'"
                    ),
                    code="PSCRIPT_INVALID_CATCH",
                    token=self.current(),
                )

            block = self.parse_suite()

            catches.append(
                CatchClause(
                    exception_type=exception_type,
                    name=name,
                    block=block,
                )
            )

            self.skip_newlines()

        # =================================
        # finally
        # =================================

        finally_block = None

        if self.match("FINALLY"):

            finally_block = self.parse_suite()

        # =================================
        # try phải có catch hoặc finally
        # =================================

        if not catches and finally_block is None:

            self.syntax_error(
                message=(
                    "Expected 'catch' or 'finally' "
                    "after try block"
                ),
                code="PSCRIPT_EXPECTED_CATCH_FINALLY",
                token=self.current(),
            )

        return TryStatement(
            try_block,
            catches,
            finally_block,
        )
        
    # ==================================================== #