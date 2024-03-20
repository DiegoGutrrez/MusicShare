import secrets
import string
import hashlib
import base64
import requests


class Spotify:
    def generate_random_string(length):
        possible = string.ascii_letters + string.digits
        values = secrets.token_bytes(length)
        return ''.join(possible[x % len(possible)] for x in values)


    def sha256(plain):
        encoder = plain.encode('utf-8')
        hashed = hashlib.sha256(encoder).digest()
        return hashed


    def base64encode(input):
        encoded = base64.b64encode(input).decode('utf-8')
        return encoded.replace('=', '').replace('+', '-').replace('/', '_')


    def get_access_token_info(url,clientId,code,redirectUri,code_verifier):

        payload = {
            'client_id': clientId,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirectUri,
            'code_verifier': code_verifier
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(url, data=payload, headers=headers)
        response_data = response.json()

        access_token_info = AccessTokenInfo(
            access_token=response_data['access_token'],
            token_type=response_data['token_type'],
            scope=response_data['scope'],
            expires_in=response_data['expires_in'],
            refresh_token=response_data['refresh_token']
        )
        
        return access_token_info



class AccessTokenInfo:
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