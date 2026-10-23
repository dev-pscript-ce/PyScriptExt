import sys
sys.dont_write_bytecode=True

class PscriptError(Exception):
    def __init__(self,message,*,code="PSCSRIPT_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code
    def __str__(self):
        return self.message

class PscriptSyntaxError(PscriptError):

    def __init__(
        self,
        message,
        line=1,
        column=1,
        length=1,
        code="PSCRIPT_PARSE_ERROR",
        token=None,
    ):

        super().__init__(
            message,
            code=code
        )

        self.line = line

        self.column = column

        self.length = length

        self.code = code

        self.token = token

    @property
    def end_column(self):
        return self.column + self.length

    @property
    def location(self):
        return f"{self.line}:{self.column}"

