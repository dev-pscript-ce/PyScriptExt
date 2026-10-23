import sys
sys.dont_write_bytecode = True

class AnalyzerProgram:
    def visit_Program(self, node):
        self.visit(node.body)