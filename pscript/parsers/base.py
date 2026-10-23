import sys
sys.dont_write_bytecode = True

from pscript.errors.pscript_errors import (
    PscriptSyntaxError,
)

class ParserBase:

    def current(self):

        return (
            self.tokens[self.pos]
            if self.pos < len(self.tokens)
            else None
        )

    def previous(self):
        if self.pos <= 0:
            return None
        return self.tokens[self.pos - 1]
    
    def get_error_position(
        self,
        token=None,
        length=None,
    ):
        """
        Trả về:

            line
            column
            length

        Tất cả dùng hệ 1-based.
        """

        if token is None:
            token = self.current()

        # =====================================
        # Có token hiện tại
        # =====================================

        if token is not None:

            line = max(
                getattr(
                    token,
                    "line",
                    1,
                ),
                1,
            )

            column = max(
                getattr(
                    token,
                    "column",
                    1,
                ),
                1,
            )

            if length is None:

                value = getattr(
                    token,
                    "value",
                    "",
                )

                if value is None:
                    length = 1

                else:
                    length = max(
                        len(
                            str(value)
                        ),
                        1,
                    )

            return (
                line,
                column,
                max(
                    length,
                    1,
                ),
            )

        # =====================================
        # EOF
        # =====================================

        if self.tokens:

            last_token = self.tokens[-1]

            line = max(
                getattr(
                    last_token,
                    "line",
                    1,
                ),
                1,
            )

            last_column = max(
                getattr(
                    last_token,
                    "column",
                    1,
                ),
                1,
            )

            last_value = getattr(
                last_token,
                "value",
                "",
            )

            value_length = max(
                len(
                    str(
                        last_value
                        or ""
                    )
                ),
                1,
            )

            column = (
                last_column
                + value_length
            )

            return (
                line,
                column,
                1,
            )

        # Không có token nào

        return (
            1,
            1,
            1,
        )

    def get_expected_position(self):
        """
        Vị trí mà parser đang mong đợi token tiếp theo.

        Trả về:
            line
            column
            length
        """

        current = self.current()

        if current is not None:

            # Nếu current không phải NEWLINE,
            # vị trí hiện tại chính là vị trí lỗi.
            if current.kind != "NEWLINE":

                return (
                    max(
                        getattr(
                            current,
                            "line",
                            1,
                        ),
                        1,
                    ),
                    max(
                        getattr(
                            current,
                            "column",
                            1,
                        ),
                        1,
                    ),
                    1,
                )

        previous = self.previous()

        if previous is not None:

            line = max(
                getattr(
                    previous,
                    "line",
                    1,
                ),
                1,
            )

            column = max(
                getattr(
                    previous,
                    "column",
                    1,
                ),
                1,
            )

            value = getattr(
                previous,
                "value",
                "",
            )

            length = max(
                len(str(value or "")),
                1,
            )

            return (
                line,
                column + length,
                1,
            )

        return (
            1,
            1,
            1,
        )

    def get_error_code(self,error):

        return getattr(
            error,
            "code",
            "PSCRIPT_PARSE_ERROR",
        )

    def syntax_error(
        self,
        message,
        code="PSCRIPT_PARSE_ERROR",
        token=None,
        length=None,
        line=None,
        column=None,
    ):
        if line is None or column is None:
            line, column, error_length = (
                self.get_error_position(
                    token=token,
                    length=length,
                )
            )
        else:
            error_length = (
                max(length,1)
                if length is not None
                else 1
            )

        raise PscriptSyntaxError(
            message=message,

            line=line,

            column=column,

            length=error_length,

            code=code,

            token=(
                token
                if token is not None
                else self.current()
            ),
        )

    def eat(
        self,
        kind,
    ):

        token = self.current()

        # =====================================
        # EOF
        # =====================================

        if token is None:

            self.syntax_error(
                message=(
                    f"Expected {kind}, "
                    "got EOF"
                ),

                code=(
                    "PSCRIPT_UNEXPECTED_EOF"
                ),

                token=None,
            )

        # =====================================
        # Sai token
        # =====================================

        if token.kind != kind:

            self.syntax_error(
                message=(
                    f"Expected {kind}, "
                    f"got {token.kind}"
                ),

                code=(
                    "PSCRIPT_EXPECTED_TOKEN"
                ),

                token=token,
            )

        self.pos += 1

        return token


    def peek(
        self,
        offset=1,
    ):

        pos = (
            self.pos
            + offset
        )

        return (
            self.tokens[pos]

            if (
                0 <= pos
                < len(self.tokens)
            )

            else None
        )


    def expect(
        self,
        *kinds,
    ):

        token = self.match(
            *kinds,
        )

        if token is not None:
            return token

        current = self.current()

        expected = " | ".join(
            kinds,
        )

        # =====================================
        # EOF
        # =====================================

        if current is None:

            self.syntax_error(
                message=(
                    f"Expected {expected}, "
                    "got EOF"
                ),

                code=(
                    "PSCRIPT_UNEXPECTED_EOF"
                ),

                token=None,
            )

        # =====================================
        # NEWLINE
        # =====================================

        if current.kind == "NEWLINE":

            line, column, error_length = (
                self.get_expected_position()
            )

            self.syntax_error(
                message=(
                    f"Expected {expected}, "
                    f"got {current.kind}"
                ),
                code=(
                    "PSCRIPT_EXPECTED_TOKEN"
                ),
                line=line,
                column=column,
                length=error_length,
                token=current,
            )

        # =====================================
        # Sai token
        # =====================================

        self.syntax_error(
            message=(
                f"Expected {expected}, "
                f"got {current.kind}"
            ),

            code=(
                "PSCRIPT_EXPECTED_TOKEN"
            ),

            token=current,
        )

    def expect_value(
        self,
        *values,
    ):

        current = self.current()

        expected = " | ".join(
            map(
                str,
                values,
            )
        )

        # =====================================
        # EOF
        # =====================================

        if current is None:

            self.syntax_error(
                message=(
                    f"Expected {expected}, "
                    "got EOF"
                ),

                code=(
                    "PSCRIPT_UNEXPECTED_EOF"
                ),

                token=None,
            )

        # =====================================
        # Sai giá trị
        # =====================================

        if current.value not in values:

            self.syntax_error(
                message=(
                    f"Expected {expected}, "
                    f"got {current.kind}"
                    f"({current.value})"
                ),

                code=(
                    "PSCRIPT_EXPECTED_KEYWORD"
                ),

                token=current,
            )

        # =====================================
        # Đúng → ăn đúng 1 token
        # =====================================

        self.pos += 1

        return current
    

    def check(
        self,
        *kinds,
        offset=0,
    ):

        token = self.peek(
            offset,
        )

        return (
            token is not None

            and token.kind in kinds
        )


    def check_value(
        self,
        *values,
        offset=0,
    ):

        token = self.peek(
            offset,
        )

        return (
            token is not None

            and token.value in values
        )


    def skip(
        self,
        *kinds,
    ):

        while self.match(
            *kinds,
        ):

            pass


    def match(
        self,
        *kinds,
    ):

        if self.check(
            *kinds,
        ):

            token = self.current()

            self.pos += 1

            return token


        return None


    def match_value(
        self,
        *values,
    ):

        if self.check_value(
            *values,
        ):

            token = self.current()

            self.pos += 1

            return token

        return None


    def skip_layout(self):

        while self.match(
            "NEWLINE",
            "INDENT",
            "DEDENT",
        ):
            pass

    def skip_newlines(self):
        while self.match("NEWLINE"):
            pass