import json
import os
import secrets
import string
import hashlib
import base64
import sys
from urllib.parse import urlencode, urljoin
import webbrowser
import requests
# import model.config
from local_web_server import StartWebServerUserAuth
from model.config import *
from model.SpotifyTokenInfo import SpotifyTokenInfo
from spotify.spotify_generic import SearchType


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

    access_token_info = SpotifyTokenInfo(
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


    

    # Genera la URL de autorización de Spotify

    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'scope': SPOTIFY_SCOPE,
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




class Spotify:

    def read_token_file(path : str) -> SpotifyTokenInfo:

        # Leer el contenido del archivo
        with open(path, 'r') as f:
            json_data = f.read()

        # Cargar el JSON
        try:
            data_dict = json.loads(json_data)
        except json.JSONDecodeError as e:
            print("Error al decodificar JSON:", e)
            exit()

        # Crear una instancia de SpotifyTokenInfo con los datos cargados desde el JSON
        spotify_access_token = SpotifyTokenInfo(
            access_token=data_dict['access_token'],
            token_type=data_dict['token_type'],
            scope=data_dict['scope'],
            expires_in=data_dict['expires_in'],
            refresh_token=data_dict['refresh_token']
        )

        return spotify_access_token



    def check_for_spotify_token_file():

        if os.path.exists(SPOTIFY_TOKEN_PATH):
            print(f"El archivo '{SPOTIFY_TOKEN_PATH}' existe.")

            return 0
        else:
            print(f"El archivo '{SPOTIFY_TOKEN_PATH}' no existe. Buscando en '{SPOTIFY_TOKEN_PATH_2}'")
            
            if os.path.exists(SPOTIFY_TOKEN_PATH_2):
                print(f"El archivo '{SPOTIFY_TOKEN_PATH_2}' existe.")

                return 1
            else:
                print(f"El archivo '{SPOTIFY_TOKEN_PATH_2}' no existe.")

                return -1


    def get_spotify_auth() -> SpotifyTokenInfo:

        res = Spotify.check_for_spotify_token_file()
        if(res == 0):
            return Spotify.read_token_file(SPOTIFY_TOKEN_PATH)
        
        elif(res == 1):
            return Spotify.read_token_file(SPOTIFY_TOKEN_PATH_2)
        
        else:
            print('El archivo con el token de Spotify ha sido eliminado, generando de nuevo...\n')

            spotify_access_token: SpotifyTokenInfo = get_spotify_token_info()

            # Abrir un archivo en modo escritura ('w')
            with open(SPOTIFY_TOKEN_PATH, 'w') as f:
                f.write(spotify_access_token.to_json())

            return spotify_access_token
            




    def get_user_id(spotify_token) -> string:

        # Encabezado de autorización con el token de acceso
        headers = {
            "Authorization": "Bearer "+ spotify_token  # Reemplaza 'tu_access_token' con tu token de acceso real
        }

        # Realizar la solicitud GET a la API de Spotify
        response = requests.get('https://api.spotify.com/v1/me', headers=headers)

        response_json = response.json()

        return response_json['uri'].split(':')[2], response_json['country']
    


    def create_playlist( user_id, token , playlist_name, description = '', public = False, collaborative = False):

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        data = {
            "name": playlist_name,
            "description": description,
            "public": public,
            "collaborative": collaborative
        }

        # Realizar la solicitud POST a la API de Spotify
        response = requests.post(f"https://api.spotify.com/v1/users/{user_id}/playlists", headers=headers, json=data)

        if response.status_code == 201:
            response_json = response.json()
            return True,response_json['id'],None
        

        error_text = ''

        if response.status_code == 401:
            error_text = 'Error -> Bad token'
        elif response.status_code == 403:
            error_text = 'Error -> Bad OAuth request'
        elif response.status_code == 429:
            error_text = 'Error -> The app has exceeded its rate limits'

        return False, None, error_text
    


    def search_track(token, query : string, type : SearchType, market: string = None, limit = 10, offset = 0):

        headers = {
            "Authorization": "Bearer "+ token
        }

        params = '?q=' + query.replace(" ", "+") 

        params += '&type=' + type.value

        if(market):
            params += '&market=' + market

        if(limit):
            params += '&limit=' + str(limit)

        if(offset):
            params += '&offset=' + str(offset)

        print('Search track: https://api.spotify.com/v1/search'+params)
        response = requests.get('https://api.spotify.com/v1/search' + params, headers=headers)

        response_json = response.json()

        if(response.status_code == 200 or response.status_code == 201):
            
            track_id = response_json['tracks']['items'][0]['uri']

            return track_id 
        
        else:
            return None



    def add_track_to_playlist(token, playlist_id, track_uri,position = None):
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # if(position):
        #     data = {
        #         "uris": [track_uri],
        #         "position": 0
        #     }
        # else:
        #     data = {
        #         "uris": [track_uri]
        #     }

        data = {
            "uris": track_uri,
            "position": 0
        }
        
        

        # Realizar la solicitud POST a la API de Spotify
        response = requests.post(f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks', headers=headers, json=data)

        if (response.status_code == 201 or response.status_code == 200):
            response_json = response.json()
            return True
        
        return False
    

    def add_tracks_to_playlist(token, playlist_id : str, track_uris: list[str],position = None):
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # if(position):
        data = {
            "uris": track_uris,
            "position": 0
        }

        # Realizar la solicitud POST a la API de Spotify
        response = requests.post(f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks', headers=headers, json=data)

        if (response.status_code == 201 or response.status_code == 200):
            response_json = response.json()
            return True
        
        return False




    def create_playlist_and_fill(token,playlist_name, tracks) -> str:

        user_id, user_country = Spotify.get_user_id(token)


        res_bool, playlist_id , error_msg = Spotify.create_playlist(user_id,token, playlist_name)

        if(res_bool == False):
            print(error_msg)
            sys.exit()


        track_uris : list[str] = []

        for track in tracks:

            track_uri = Spotify.search_track(token, track, SearchType.track, user_country, 4)
            if(track_uri != None):
                track_uris.append(track_uri)


        # track_uris = [
        #             "spotify:track:2DNyZP4Py6f4zMASLBnIu6",
        #             "spotify:track:4waqcUQWdj0yH26STWl2Rq",
        #             "spotify:track:1YtZ6sHC4TalQbK4c37bqJ",
        #             "spotify:track:1I3O8YESvj6G6TqHaJTvEU",
        #             "spotify:track:0Zbm5CKG9HHT9bwgvFc0qI",
        #             "spotify:track:6GvgQAIyf4F3IirbbctB1x",
        #             "spotify:track:6ZzMVEVTBhekYNKTGxCoUt",
        #             "spotify:track:1j8z4TTjJ1YOdoFEDwJTQa"]


        Spotify.add_tracks_to_playlist(token,playlist_id,track_uris)

        return playlist_id
