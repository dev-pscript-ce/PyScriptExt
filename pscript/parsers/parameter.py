import sys
sys.dont_write_bytecode = True

from ..asts.parameters import Parameter
from ..parameter_kind.paramkind import ParameterKind

class ParseParameter:

    def parse_parameter(
        self,
        keyword_only=False,
        allow_varargs=True,
    ):

        #
        # *args
        #

        if (
            allow_varargs
            and self.match("STAR")
        ):
            name_token= self.expect("IDENT")

            return Parameter(
                name=name_token.value,
                kind=(
                    ParameterKind
                    .VAR_POSITIONAL
                ),
                token=name_token,
            )

        #
        # **kwargs
        #

        if (
            allow_varargs
            and self.match("DOUBLESTAR")
        ):
            name_token = self.expect("IDENT")

            return Parameter(
                name=name_token.value,
                kind=(
                    ParameterKind
                    .VAR_KEYWORD
                ),
                token=name_token,
            )

        #
        # normal parameter
        #

        name_token = self.expect(
            "IDENT"
        )

        default = None

        if self.match("EQUAL"):

            default = (
                self.parse_expression()
            )

        return Parameter(
            name=name_token.value,

            default=default,

            kind=(
                ParameterKind
                .KEYWORD_ONLY

                if keyword_only

                else

                ParameterKind
                .POSITIONAL
            ),
            token=name_token
        )


    def parse_parameter_list(
        self,
        allow_varargs=True,
        ):


        params = []

        keyword_only = False

        has_varargs = False

        has_varkw = False

        # =================================
        # (
        # =================================

        self.expect(
            "LPAREN",
        )

        # Hỗ trợ:
        #
        # func test(
        #     name1,
        #     name2
        # )
        #
        self.skip_layout()

        # =================================
        # Parameters
        # =================================

        while not self.check(
            "RPAREN",
        ):

            # -----------------------------
            # Keyword-only marker
            #
            # func test(
            #     name,
            #     *,
            #     option
            # )
            # -----------------------------

            if (
                allow_varargs
                and self.check("STAR")
                and self.check(
                    "COMMA",
                    offset=1,
                )
            ):

                marker=self.expect(
                    "STAR",
                )

                self.expect(
                    "COMMA",
                )

                if keyword_only:

                    self.syntax_error(
                        message=(
                            "Duplicate '*' "
                            "in parameter list"
                        ),
                        code=(
                            "PSCRIPT_DUPLICATE_KEYWORD_MARKER"
                        ),
                        token=marker
                    )

                keyword_only = True

                self.skip_layout()

                continue

            # -----------------------------
            # Parse parameter
            # -----------------------------

            param = self.parse_parameter(
                keyword_only=keyword_only,
                allow_varargs=allow_varargs,
            )

            # -----------------------------
            # Validate parameter
            # -----------------------------

            if (
                param.kind
                == ParameterKind.VAR_POSITIONAL
            ):

                if has_varargs:

                    self.syntax_error(
                        message=(
                            "Multiple *args "
                            "parameters"
                        ),
                        code=(
                            "PSCRIPT_MULTIPLE_VARARGS"
                        ),
                    )

                if has_varkw:

                    self.syntax_error(
                        message=(
                            "*args cannot appear "
                            "after **kwargs"
                        ),
                        code=(
                            "PSCRIPT_VARARGS_AFTER_VARKW"
                        ),
                    )

                has_varargs = True

                # Sau *args, các parameter
                # tiếp theo là keyword-only.
                keyword_only = True

            elif (
                param.kind
                == ParameterKind.VAR_KEYWORD
            ):

                if has_varkw:

                    self.syntax_error(
                        message=(
                            "Multiple **kwargs "
                            "parameters"
                        ),
                        code=(
                            "PSCRIPT_MULTIPLE_VARKW"
                        ),
                    )

                has_varkw = True

            elif has_varkw:

                self.syntax_error(
                    message=(
                        "Parameter cannot appear "
                        "after **kwargs"
                    ),
                    code=(
                        "PSCRIPT_PARAMETER_AFTER_VARKW"
                    ),
                )

            params.append(
                param,
            )

            # -----------------------------
            # Không có dấu ,
            # kết thúc parameter list
            # -----------------------------

            if not self.match(
                "COMMA",
            ):
                break

            # Hỗ trợ xuống dòng sau dấu ,
            #
            # name1,
            # name2
            #
            self.skip_layout()

            # Hỗ trợ trailing comma:
            #
            # name1,
            # name2,
            # )
            #
            if self.check(
                "RPAREN",
            ):
                break

        # =================================
        # )
        # =================================

        self.skip_layout()

        self.expect(
            "RPAREN",
        )

        return params