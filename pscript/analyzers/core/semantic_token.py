import sys
sys.dont_write_bytecode = True

class AddSemanticToken:

    def add_semantic_token(
        self,
        node,
        token_type,
    ):
        token = getattr(
            node,
            "token",
            None,
        )

        if token is None:
            return

        self.semantic_tokens.append(
            {
                "token": token,
                "type": token_type,
            }
        )