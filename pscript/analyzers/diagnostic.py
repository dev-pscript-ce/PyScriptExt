import sys,json
sys.dont_write_bytecode = True

def get_diagnostic(source):
    from .api import analyze_source
    return analyze_source(source).diagnostics

def main():
    try:
        source = sys.stdin.read()
        print(
            json.dumps(
                get_diagnostic(source),
                ensure_ascii=False,
            )
        )
    except Exception as error:
        print(
            json.dumps(
                {"error": str(error)},
                ensure_ascii=False,
            )
        )

if __name__ == "__main__":
    main()
