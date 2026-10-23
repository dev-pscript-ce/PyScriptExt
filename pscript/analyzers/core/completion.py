import sys
sys.dont_write_bytecode = True

def is_incomplete_syntax_error( self,source, error, ):
    message = str(error) 
    incomplete_messages = ( "Expected IDENT, got EOF", "Expected IDENT, got NEWLINE", "Expected expression, got EOF", ) 
    if not any( text in message for text in incomplete_messages ): 
        return False 
    line = getattr( error, "line", None, )
    if line is None: 
        return False 
    lines = source.splitlines() 
    if not lines: 
        return False 
    if line != len(lines): 
        return False 
    return True