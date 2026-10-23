import sys
sys.dont_write_bytecode=True

from pscript.scanners.scanner import Scanner
from pscript.parsers.parser import Parser

from pscript.analyzers.core import(
    ScopeManager,
    AnalyzerBase,
    Resolver,
    DiagnosticError,
    AddSemanticToken,
    is_incomplete_syntax_error,
)
from pscript.analyzers.visitors import (
    AnalyzerProgram,
    AnalyzerClasses,
    AnalyzerExprs,
    AnalyzerFunctions,
    AnalyzerStmts,
    AnalyzerImports,
    
)
from pscript.analyzers.validates import(
    ValidateArgument,
    ValidateFunctionCall,
    ValidateMemberAccess,

)

# =====================================
# AST Analyzer
# =====================================

class AnalyzerSource(
    AnalyzerBase,

    AnalyzerProgram,
    AnalyzerClasses,
    AnalyzerExprs,
    AnalyzerFunctions,
    AnalyzerStmts,
    AnalyzerImports,

    ValidateMemberAccess,
    ValidateArgument,
    ValidateFunctionCall,

    Resolver,
    DiagnosticError,
    AddSemanticToken,
    
):

    def __init__(
        self,
        source="",
        *,
        diagnostics=None,
    ):
        self.source = source or ""
        self.diagnostics = diagnostics if diagnostics is not None else []

        self.tokens = []
        self.tree = None

        self.scopes = ScopeManager()
        self.module_aliases = {}
        self.imported_modules = set()
        self.current_class = None
        self.semantic_tokens = []

        self.error = None
        self.error_stage = None

    # =====================================
    # Source pipeline|Phân tích AST/Source
    # =====================================

    def analyze(self, source=None):
        """
        Shared source pipeline:
        Scanner -> Parser -> AST analyzer.

        The returned analyzer contains all source context required by
        diagnostic, hover, completion and signature providers.
        """
        if source is not None:
            self.source = source

        self.tokens = []
        self.tree = None
        self.error = None
        self.error_stage = None

        # Reusable AnalyzerSource: reset source-dependent state.
        self.diagnostics.clear()
        self.scopes = ScopeManager()
        self.module_aliases.clear()
        self.imported_modules.clear()
        self.current_class = None
        self.semantic_tokens.clear()

        try:
            self.tokens = Scanner(self.source).scan()
        except Exception as error:
            self.error = error
            self.error_stage = "scanner"
            self.add_error(
                line=getattr(error, "line", 1),
                column=getattr(error, "column", 1),
                length=getattr(error, "length", 1),
                message=str(error),
                code=getattr(error, "code", "PSCRIPT_SCAN_ERROR"),
            )
            return self

        try:
            self.tree = Parser(self.tokens).parse()
        except Exception as error:
            self.error = error
            self.error_stage = "parser"

            if is_incomplete_syntax_error(self.source, error):
                return self

            self.add_error(
                line=getattr(error, "line", 1),
                column=getattr(error, "column", 1),
                length=getattr(error, "length", 1),
                message=str(error),
                code=getattr(error, "code", "PSCRIPT_PARSE_ERROR"),
            )
            return self

        try:
            self.visit(self.tree)
        except Exception as error:
            self.error = error
            self.error_stage = "analyzer"
            self.add_error(
                line=1,
                column=1,
                length=1,
                message=f"Analyzer error: {error}",
                code="PSCRIPT_ANALYZER_ERROR",
            )

        return self

    # Backward-compatible AST entry point.
    def diagnostic(self, tree):
        self.visit(tree)
        return self

    





