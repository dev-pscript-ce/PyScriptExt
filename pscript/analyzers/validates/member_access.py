import sys
sys.dont_write_bytecode = True

from pscript.asts.expressions import MemberAccess

class ValidateMemberAccess:
    
    def validate_MemberAccess(
            self,
            call,
        ):

            callee = call.callee

            if not isinstance(
                callee,
                MemberAccess,
            ):
                return

            # Resolve toàn bộ member chain
            result = self.resolve_member_chain(
                callee
            )

            if result is None:
                return

            # result là method metadata
            self.validate_arguments(
                call=call,
                method=result,
                function_name=self.member_chain_name(
                    callee
                ),
            )

