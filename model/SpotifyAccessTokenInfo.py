

class SpotifyAccessTokenInfo:
    def __init__(self, access_token, token_type, scope, expires_in, refresh_token):
        self.access_token = access_token
        self.token_type = token_type
        self.scope = scope
        self.expires_in = expires_in
        self.refresh_token = refresh_token

    def to_dict(self):
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "scope": self.scope,
            "expires_in": self.expires_in,
            "refresh_token": self.refresh_token
        }

    def to_json(self):
        import json
        return json.dumps(self.to_dict())