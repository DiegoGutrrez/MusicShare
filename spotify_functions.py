import json
import os
import secrets
import string
import hashlib
import base64
from urllib.parse import urlencode, urljoin
import webbrowser
import requests
# import model.config
from local_web_server import StartWebServerUserAuth
from model.config import *
from model.SpotifyAccessTokenInfo import SpotifyAccessTokenInfo


# class Spotify:
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

    access_token_info = SpotifyAccessTokenInfo(
        access_token=response_data['access_token'],
        token_type=response_data['token_type'],
        scope=response_data['scope'],
        expires_in=response_data['expires_in'],
        refresh_token=response_data['refresh_token']
    )
    
    return access_token_info



def get_spotify_token_info():

    spotify_url= 'https://accounts.spotify.com'
    auth_url = '/authorize'
    access_token_url = '/api/token'


    code_verifier = generate_random_string(64)
    hashed = sha256(code_verifier)
    codeChallenge = base64encode(hashed)


    scope = 'user-read-private user-read-email'

    # Genera la URL de autorización de Spotify

    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'scope': scope,
        'code_challenge_method': 'S256',
        'code_challenge': codeChallenge,
        'redirect_uri': REDIRECT_URI
    }
    auth_url_with_params = urljoin(spotify_url + auth_url, '?' + urlencode(params))

    # Almacena el code_verifier en el almacenamiento local (si es necesario)
    # Nota: en Python no hay un equivalente directo de window.localStorage, 
    # así que aquí solo se está simulando el almacenamiento temporal
    # os.environ['code_verifier'] = code_verifier

    # Redirige al usuario a la URL de autorización de Spotify
    webbrowser.open(auth_url_with_params)

    authorization_code, state = StartWebServerUserAuth(8888)

    return get_access_token_info(spotify_url + access_token_url, CLIENT_ID, authorization_code, REDIRECT_URI, code_verifier)



def get_spotify_auth() -> SpotifyAccessTokenInfo:

    if os.path.exists(SPOTIFY_TOKEN_PATH):
        print(f"El archivo '{SPOTIFY_TOKEN_PATH}' existe.")

        # Leer el contenido del archivo
        with open(SPOTIFY_TOKEN_PATH, 'r') as f:
            json_data = f.read()

        # Cargar el JSON
        try:
            data_dict = json.loads(json_data)
        except json.JSONDecodeError as e:
            print("Error al decodificar JSON:", e)
            exit()

        # Crear una instancia de SpotifyAccessTokenInfo con los datos cargados desde el JSON
        spotify_access_token = SpotifyAccessTokenInfo(
            access_token=data_dict['access_token'],
            token_type=data_dict['token_type'],
            scope=data_dict['scope'],
            expires_in=data_dict['expires_in'],
            refresh_token=data_dict['refresh_token']
        )

    else:
        print(f"El archivo '{SPOTIFY_TOKEN_PATH}' no existe.")
        spotify_access_token: SpotifyAccessTokenInfo = get_spotify_token_info()

        # Abrir un archivo en modo escritura ('w')
        with open(SPOTIFY_TOKEN_PATH, 'w') as f:
            f.write(spotify_access_token.to_json())

    return spotify_access_token