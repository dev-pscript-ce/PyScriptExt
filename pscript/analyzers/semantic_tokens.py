import sys
import json

from pscript.scanners.scanner import Scanner
from pscript.parsers import Parser
from .api import analyze_tree


def main():

    try:

        source = sys.stdin.read()

        scanner = Scanner(
            source,
        )

        tokens = scanner.scan()


        parser = Parser(
            tokens,
        )

        tree = parser.parse()

        # =================================
        # AST analyzer
        # =================================

        diagnostics = []

        semantic_tokens = analyze_tree(
            tree,
            diagnostics,
        )

        result = []

        for item in semantic_tokens:

            token = item["token"]

            result.append(
                {
                    "line": token.line,
                    "column": token.column,
                    "length": token.length,
                    "type": item["type"],
                }
            )
        # =================================
        # JSON OUTPUT
        # =================================

        print(
            json.dumps(
                result,
                ensure_ascii=False,
            )
        )


    except Exception as error:

        print(
            json.dumps(
                {
                    "error": str(error),
                },
                ensure_ascii=False,
            )
        )

def parse_semantic_tokens():
    # =================================
    # Source
    # =================================

    source = sys.stdin.read()


    # =================================
    # Scanner
    # =================================

    scanner = Scanner(
        source,
    )

    tokens = scanner.scan()


    # =================================
    # Parser
    # =================================

    parser = Parser(
        tokens,
    )

    tree = parser.parse()


    # =================================
    # AST analyzer
    # =================================

    diagnostics = []

    semantic_tokens = analyze_tree(
        tree,
        diagnostics,
    )
    return semantic_tokens

def islist(semantic_tokens):

    print(
        f"[SemanticTokens] count = {len(semantic_tokens)}",
        file=sys.stderr,
    )

    for i, item in enumerate(semantic_tokens):

        token = item["token"]

        print(
            f"[{i:02}] "
            f"line={token.line} "
            f"column={token.column} "
            f"length={token.length} "
            f"type={item['type']}",
            file=sys.stderr,
        )
    
def isdict(semantic_tokens):

    result = []

    for item in semantic_tokens:

        token = item["token"]

        result.append(
            {
                "line": token.line,
                "column": token.column,
                "length": token.length,
                "type": item["type"],
            }
        )
    return result

def main_debug():
    log_dict=False
    try:
        semantic_tokens = parse_semantic_tokens()

        # DEBUG LIST
        if not log_dict:
            islist(semantic_tokens)
        result = isdict(semantic_tokens)

        # DEBUG DICT
        if log_dict:
            print(
                "[SemanticTokens] dict:",
                file=sys.stderr,
            )
            print(
                json.dump(
                    result,
                    ensure_ascii=False,
                    indent=2,
                ),
                file=sys.stderr,
            )
            
        # =================================
        # JSON OUTPUT
        # =================================
        print(
            json.dumps(
                result,
                ensure_ascii=False,
            )
        )

    except Exception as error:

        print(
            json.dumps(
                {
                    "error": str(error),
                },
                ensure_ascii=False,
            )
        )
        
if __name__ == "__main__":
    main()