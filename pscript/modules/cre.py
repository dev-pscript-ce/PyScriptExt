class CreateFileModule:
    def __init__(self,engine):
        self.engine = engine

    def CREATE_FILE(self,file_name,ext):
        return self.engine._create_file(file_name,ext)