
STATEMENTS = {}

def statement(kind):

    def wrapper(func):

        STATEMENTS[kind] = func

        return func

    return wrapper


