
def build_statement_parsers(parser):

    return {
        "IMPORT": parser.parse_import,
        "FROM": parser.parse_from_import,
        "RETURN": parser.parse_return,
        "FUNC": parser.parse_function,
        "IF": parser.parse_if,
        "WHILE": parser.parse_while,
        "FOR": parser.parse_for,
        "BREAK": parser.parse_break,
        "CONTINUE": parser.parse_continue,
    }