import sys
sys.dont_write_bytecode = True

SEMANTIC_TOKEN_KINDS = {
    "user_defined_class": "class",
    "user_defined_function": "function",
    "user_defined_method": "method",
    "variable": "variable",
    "params": "parameter",
}