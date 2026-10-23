import sys
sys.dont_write_bytecode = True

from pscript.asts.program import Program

from ..tokens.token_type import TokenType

from .base import ParserBase
from .literal import LiteralParser
from .expression import ExpressionParser
from .statement import StatementParser
from .function import(
    DeclarationParser,
    AnonymousParse
)
from .class_p import ClassParser,Instantiate

from.import_p import ImportParse
from .argument import Arguments
from.parameter import ParseParameter
from pscript.scanners.scanner import Scanner

# from .parser_map import  build_statement_parsers

from pscript.helpers_ps.wrapper_statement import*

class Parser(
    ParserBase,
    LiteralParser,
    ExpressionParser,
    StatementParser,
    DeclarationParser,
    AnonymousParse,
    ImportParse,
    Arguments,
    ParseParameter,
    ClassParser,
    Instantiate

):
    def __init__(self, tokens):

        self.tokens = list(tokens)

        self.pos = 0

        # self.statement_parsers = build_statement_parsers(self)           

    def parse_embedded_expression(self, source):

        scanner = Scanner(source)

        tokens = scanner.scan()

        parser = Parser(tokens)

        return parser.parse_expression()

    def parse(self):

        body = []
        
        while self.current() is not None:
            
            while (
                self.current() and
                self.current().kind == TokenType.NEWLINE
            ):
                
                self.eat(TokenType.NEWLINE)
            
            
            if self.current() is None:
                break

            body.append(
                self.parse_statement()
            )

        return Program(body)       
    
# ----------------------------------------------------------- #