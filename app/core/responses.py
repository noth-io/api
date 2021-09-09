def generate_auth_response(token: str, token_type: str):
    return {
        "auth_token": token,
        "token_type": token_type,
    }