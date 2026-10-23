import sys
sys.dont_write_bytecode = True

from .analyzer import AnalyzerSource

def analyze_source(source="", diagnostics=None):
    
    return AnalyzerSource(
        source,
        diagnostics=diagnostics,
    ).analyze()

def analyze_tree(
    tree,
    diagnostics,
):
    analyzer = AnalyzerSource(
        diagnostics,
    )

    analyzer.diagnostic(
        tree,
    )

    return analyzer.semantic_tokens

