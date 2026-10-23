import sys
sys.dont_write_bytecode = True

from ..helpers_ps.wrapper_statement import statement
from ..asts.imports import (Import,FromImport)

class ImportParse:
    
    @statement("IMPORT")
    # Hỗ trợ multiline
    def parse_import(self):

        import_token = self.expect("IMPORT")

        imports = []

        # =====================================
        # import (
        #     cv2
        #     ocr
        # )
        # =====================================

        multiline = self.match("LPAREN")

        while True:

            # ---------------------------------
            # Bỏ qua newline trong (...)
            # ---------------------------------

            if multiline:
                self.skip_layout()

                # import (
                # )
                if self.check("RPAREN"):
                    self.expect("RPAREN")
                    break

            # =====================================
            # import "abc.ps"
            # =====================================

            if self.check("STRING"):

                module_token = self.expect(
                    "STRING"
                )

                module = module_token.value
                is_file = True

            # =====================================
            # import cv2
            # =====================================

            else:

                module_token = self.expect(
                    "IDENT"
                )

                module = module_token.value
                is_file = False

            alias = None

            # =====================================
            # import cv2 as c
            # =====================================

            if self.match("AS"):

                alias = self.expect(
                    "IDENT"
                ).value

            imports.append(
                (
                    module,
                    alias,
                    is_file,
                )
            )

            # =====================================
            # import cv2, ocr
            # =====================================

            if self.match("COMMA"):

                # Cho phép:
                #
                # import (
                #     cv2,
                #     ocr,
                # )
                #
                if multiline:
                    self.skip_layout()

                    if self.check("RPAREN"):
                        self.expect("RPAREN")
                        break

                continue

            # =====================================
            # multiline:
            #
            # import (
            #     cv2
            #     ocr
            # )
            # =====================================

            if multiline:

                # newline giữa các import
                if self.match("NEWLINE"):
                    continue

                # kết thúc (...)
                if self.match("RPAREN"):
                    break

                # Không phải comma, newline hoặc )
                self.error(
                    "Expected ',', newline, or ')'"
                )

            # =====================================
            # import cv2, ocr
            # =====================================

            break

        return Import(
            imports=imports,
            token=import_token,
        )

    # @statement("IMPORT")
    # def parse_import(self):

    #     import_token = self.expect(
    #         "IMPORT"
    #     )

    #     imports = []

    #     while True:

    #         # =====================================
    #         # import "abc.ps"
    #         # =====================================

    #         if self.check("STRING"):

    #             module_token = self.expect(
    #                 "STRING"
    #             )

    #             module = module_token.value
    #             is_file = True

    #         # =====================================
    #         # import cv2
    #         # =====================================

    #         else:

    #             module_token = self.expect(
    #                 "IDENT"
    #             )

    #             module = module_token.value
    #             is_file = False


    #         alias = None

    #         # =====================================
    #         # import cv2 as c
    #         # =====================================

    #         if self.match("AS"):

    #             alias = self.expect(
    #                 "IDENT"
    #             ).value


    #         imports.append(
    #             (
    #                 module,
    #                 alias,
    #                 is_file,
    #             )
    #         )


    #         # =====================================
    #         # import cv2, ocr
    #         #             ^
    #         # =====================================

    #         if not self.match("COMMA"):
    #             break


    #     return Import(
    #         imports=imports,
    #         token=import_token,
    #     )
    
    @statement("FROM")

    def parse_from_import(self):

        self.expect("FROM")

        #
        # from "./math.ps"
        #

        if self.check("STRING"):

            module = self.expect("STRING").value

        else:

            parts = []

            #
            # .  ..  ...
            #

            while self.match("DOT"):
                parts.append(".")

            #
            # math
            # core
            #

            if self.check("IDENT"):

                parts.append(
                    self.expect("IDENT").value
                )

                while self.match("DOT"):

                    parts.append(".")

                    parts.append(
                        self.expect("IDENT").value
                    )

            #
            # build module name
            #

            module = ""

            for part in parts:

                if part == ".":

                    module += "."

                else:

                    if (
                        module
                        and not module.endswith(".")
                    ):
                        module += "."

                    module += part

        #
        # from cv2 IMPORT ...
        #

        self.expect("IMPORT")

        names = []

        #
        # from cv2 import (
        #     find_click,
        #     click,
        # )
        #

        multiline = self.match("LPAREN")

        #
        # import *
        #

        if self.match("STAR"):

            names.append(("*", None))

            #
            # cho phép:
            #
            # from cv2 import (
            #     *
            # )
            #

            if multiline:
                self.expect("RPAREN")

        else:

            while True:

                #
                # Bỏ newline bên trong (...)
                #

                if multiline:
                    self.skip_layout()

                    #
                    # from cv2 import (
                    # )
                    #

                    if self.check("RPAREN"):
                        self.expect("RPAREN")
                        break

                #
                # tên member
                #

                name = self.expect("IDENT").value

                alias = None

                #
                # find_click as fc
                #

                if self.match("AS"):

                    alias = self.expect(
                        "IDENT"
                    ).value

                names.append(
                    (name, alias)
                )

                #
                # comma
                #

                if self.match("COMMA"):

                    if multiline:

                        #
                        # Cho phép trailing comma:
                        #
                        # (
                        #     cv2,
                        # )
                        #

                        self.skip_layout()

                        if self.check("RPAREN"):

                            self.expect("RPAREN")
                            break

                    continue

                #
                # multiline: không bắt buộc comma
                #
                # from cv2 import (
                #     find_click
                #     click
                # )
                #

                if multiline:

                    if self.match("NEWLINE"):
                        continue

                    if self.match("RPAREN"):
                        break

                    self.error(
                        "Expected ',', newline, or ')'"
                    )

                #
                # single-line
                #

                break

        return FromImport(
            module,
            names,
        )

    # @statement("FROM")
    # def parse_from_import(self):

    #     self.expect("FROM")

    #     #
    #     # from "./math.ps"
    #     #

    #     if self.check("STRING"):

    #         module = self.expect("STRING").value

    #     else:

    #         parts = []

    #         #
    #         # .  ..  ...
    #         #

    #         while self.match("DOT"):
    #             parts.append(".")

    #         #
    #         # math
    #         # core
    #         #

    #         if self.check("IDENT"):

    #             parts.append(
    #                 self.expect("IDENT").value
    #             )

    #             while self.match("DOT"):

    #                 parts.append(".")

    #                 parts.append(
    #                     self.expect("IDENT").value
    #                 )

    #         #
    #         # build module name
    #         #

    #         module = ""

    #         for part in parts:

    #             if part == ".":

    #                 module += "."

    #             else:

    #                 if (
    #                     module
    #                     and not module.endswith(".")
    #                 ):
    #                     module += "."

    #                 module += part

    #     self.expect("IMPORT")

    #     names = []

    #     if self.match("STAR"):

    #         names.append(("*", None))

    #     else:

    #         while True:

    #             name = self.expect("IDENT").value

    #             alias = None

    #             if self.match("AS"):
    #                 alias = self.expect("IDENT").value

    #             names.append((name, alias))

    #             if not self.match("COMMA"):
    #                 break
    #     return FromImport(module, names)