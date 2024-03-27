import cProfile
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import threading
import requests
import json
import os
import secrets
import string
import hashlib
import base64
import sys
import time
from urllib.parse import urlencode, urljoin
import webbrowser
from general_config import logging

# import model.config
from local_web_server import StartWebServerUserAuth
from model.config import *
from model.SpotifyTokenInfo import SpotifyTokenInfo
from spotify.model.Playlist import Playlist
from spotify.spotify_generic import SearchType
from model.global_variables import *

thread_local = threading.local()


def get_session() -> requests.Session:
        if not hasattr(thread_local,'session'):
            thread_local.session = requests.Session()
        return thread_local.session



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
        'client_id': SPOTIFY_CLIENT_ID,
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

    return get_access_token_info(spotify_url + access_token_url, SPOTIFY_CLIENT_ID, authorization_code, REDIRECT_URI, code_verifier)




class Spotify:


    # Manejar el error de token caducado para no tener que reiniciar la app
    def error_401():
        input('El token ha caducado, por favor, reinicie la aplicación.')
        sys.exit()  

    
    def exceeded_rate_limits():
        "Función a ejecutar cuando se recibe un error 429"

        input('Se ha llegado al límite de solicitudes de la aplicación.')
        
        sys.exit()

    
    def delete_oauth_file_and_restart():
        "Función a ejecutar cuando se recibe un error 403"

        try:
            os.remove(SPOTIFY_TOKEN_PATH)
        except Exception as e:
            print()

        input('No ha sido posible obtener el nuevo token para acceder a Spotify, por favor, reinicie la aplicación.')

        sys.exit()  



    def check_if_expired_token(spotify_token : SpotifyTokenInfo):

        headers = {
            "Authorization": "Bearer "+ spotify_token.access_token 
        }

        response = requests.get('https://api.spotify.com/v1/me', headers=headers)

        response_json = response.json()

        if(response.status_code != 200):
            if(response_json['error']['status'] == 401):
                print('El token de Spotify ha caducado, obteniendo uno nuevo...')
                Spotify.refresh_token(spotify_token)

        else:
            dif = time.time() - spotify_token.time_obtained
            if(dif > 1800):
               Spotify.refresh_token(spotify_token) 
        



    def refresh_token(spotify_token : SpotifyTokenInfo):

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': spotify_token.refresh_token,
            'client_id': SPOTIFY_CLIENT_ID
        }

        response = requests.post(f"https://accounts.spotify.com/api/token", headers=headers, data=data)

        if response.status_code == 200:
            response_data = response.json()

            spotify_token.access_token=response_data['access_token']
            spotify_token.token_type=response_data['token_type']
            spotify_token.scope=response_data['scope']
            spotify_token.expires_in=response_data['expires_in']
            spotify_token.refresh_token=response_data['refresh_token']
            spotify_token.time_obtained = time.time()

            with open(SPOTIFY_TOKEN_PATH, 'w') as f:
                f.write(spotify_token.to_json())
        
        else:
            Spotify.delete_oauth_file_and_restart()
                      


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
            


    def get_user_info(spotify_token : SpotifyTokenInfo) -> string:

        # Encabezado de autorización con el token de acceso
        headers = {
            "Authorization": "Bearer "+ spotify_token.access_token  # Reemplaza 'tu_access_token' con tu token de acceso real
        }

        # Realizar la solicitud GET a la API de Spotify
        response = requests.get('https://api.spotify.com/v1/me', headers=headers)

        response_json = response.json()

        if response.status_code == 201 or response.status_code == 200:
            return response_json['uri'].split(':')[2], response_json['country']
        else:
            if response_json['error']['status'] == 401:
                Spotify.error_401()
            elif response_json['error']['status'] == 403:
                Spotify.delete_oauth_file_and_restart()
            elif response_json['error']['status'] == 429:
                Spotify.exceeded_rate_limits()
            else:
                logging.error(response)
                sys.exit()
            return None
        
    
        


    def create_playlist( user_id, token : SpotifyTokenInfo , playlist_name, description = '', public = False, collaborative = False):

        headers = {
            "Authorization": f"Bearer {token.access_token}",
            "Content-Type": "application/json"
        }

        data = {
            "name": playlist_name,
            "description": description,
            "public": public,
            "collaborative": collaborative
        }

        response = requests.post(f"https://api.spotify.com/v1/users/{user_id}/playlists", headers=headers, json=data)
        
        response_json = response.json()
        
        if response.status_code == 201 or response.status_code == 200:
            return response_json['id']
        else:
            if response_json['error']['status'] == 401:
                Spotify.error_401()
            elif response_json['error']['status'] == 403:
                Spotify.delete_oauth_file_and_restart()
            elif response_json['error']['status'] == 429:
                Spotify.exceeded_rate_limits()
            else:
                logging.error(response)
                sys.exit()
            return None

    


    def search_track(token : SpotifyTokenInfo, query : string, type : SearchType, market: string = None, limit = 10, offset = 0):

        headers = {
            "Authorization": "Bearer "+ token.access_token
        }

        params = '?q=' + query.replace(" ", "+") 

        params += '&type=' + type.value

        if(market):
            params += '&market=' + market

        if(limit):
            params += '&limit=' + str(limit)

        if(offset):
            params += '&offset=' + str(offset)

        print(f'Buscando "{query}" en Spotify...')
        # print('Search track: https://api.spotify.com/v1/search'+params)
        response = requests.get('https://api.spotify.com/v1/search' + params, headers=headers)

        response_json = response.json()

        if(response.status_code == 200 or response.status_code == 201):
            
            track_id = response_json['tracks']['items'][0]['uri']

            return track_id 
        
        else:
            return None


    

    

    def search_track_id(token : SpotifyTokenInfo, track : str, market: string = None, limit = 4, offset = 0):
        
        session = get_session()
        
        headers = {
            "Authorization": "Bearer "+ token.access_token
        }

        params = '?q=' + track.replace(" ", "+") 

        params += '&type=track'

        if(market):
            params += '&market=' + market

        if(limit):
            params += '&limit=' + str(limit)

        if(offset):
            params += '&offset=' + str(offset)
        
        with session.get('https://api.spotify.com/v1/search' + params, headers=headers) as response:
            response_json = response.json()

            if(response.status_code == 200 or response.status_code == 201):
                
                track_id = response_json['tracks']['items'][0]['uri']

                return track_id 
            
            else:
                if(response.status_code == 429):
                    time.sleep(5)
                    return Spotify.search_track_id(token,track,market,limit,offset)
                return None

    
    
    def search_tracks_with_name(token : SpotifyTokenInfo, tracks : list, user_country : str):
        
        total_requests = len(tracks)
        total_responses = 0
        
        print('Buscando canciones en Spotify\n')
        def print_progress(total_responses, total_requests):
            print(f"\r{total_responses}/{total_requests}", end="", flush=True)
        
        tracks_ids = []
        
        before = time.time()
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = []
            for track in tracks:
                future = executor.submit(Spotify.search_track_id,token, track, user_country)
                futures.append((track, future))

            for track, future in futures:
                result = future.result()
                if(result):
                    tracks_ids.append(result)
                
                total_responses += 1
                print_progress(total_responses, total_requests)
        
        after = time.time()
        
        logging.debug('Spotify.search_tracks_with_name -> '+str(after-before)+'ms')

        print('\rBúsqueda completada\n')   
        return tracks_ids
    
        
    def create_playlist_and_fill_with_names(token : SpotifyTokenInfo, playlist_name : str, initial_tracks : list[str]):
        
        user_id, user_country = Spotify.get_user_info(token)
        
        # cProfile.run('Spotify.search_tracks_with_name2()')
        
        tracks_ids = Spotify.search_tracks_with_name(token,initial_tracks,user_country)
        
        print('Creando playlist\n')
        playlist_id = Spotify.create_playlist(user_id, token, playlist_name)
        
        if(len(tracks_ids) > 100):

            for i in range(0, len(tracks_ids), 100):
                
                track_sublist = tracks_ids[i:i+100]
                
                if Spotify.add_tracks_to_playlist(token,playlist_id,track_sublist,None) == False:
                    input('Se ha producido un error al crear la playlist en Spotify')
                    sys.exit()

        else:
            if Spotify.add_tracks_to_playlist(token,playlist_id,tracks_ids,None) == False:
                input('Se ha producido un error al crear la playlist en Spotify')
                sys.exit()
                
        print('Playlist creada con éxito\n')
    
        

    def add_track_to_playlist(token : SpotifyTokenInfo, playlist_id, track_uri,position = None):
        headers = {
            "Authorization": f"Bearer {token.access_token}",
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
    

    def add_tracks_to_playlist(token : SpotifyTokenInfo, playlist_id : str, track_uris: list[str],position = None):

        before = time.time()
        
        headers = {
            "Authorization": f"Bearer {token.access_token}",
            "Content-Type": "application/json"
        }

        if(position):
            data = {
                "uris": track_uris,
                "position": 0
            }
        else:
            data = {
                "uris": track_uris
            }

        response = requests.post(f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks', headers=headers, json=data)

        after = time.time()
        
        logging.debug('Spotify.add_tracks_to_playlist -> '+str(after-before)+'ms')
        
        response_json = response.json()
        
        if response.status_code == 201 or response.status_code == 200:
            return True
        else:
            if response_json['error']['status'] == 401:
                Spotify.error_401()
            elif response_json['error']['status'] == 403:
                Spotify.delete_oauth_file_and_restart()
            elif response_json['error']['status'] == 429:
                Spotify.exceeded_rate_limits()
            else:
                logging.error(response)
            return False





    def create_playlist_and_fill(token : SpotifyTokenInfo,playlist_name, tracks) -> str:

        user_id, user_country = Spotify.get_user_info(token)


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

        print('\nAñadiendo canciones a la lista de Spotify\n')
        Spotify.add_tracks_to_playlist(token,playlist_id,track_uris)

        return playlist_id
    


    def fetch_playlists(token : SpotifyTokenInfo,offset):
        
        headers = { "Authorization": "Bearer "+ token.access_token}

        params = {
            'limit': 50,
            'offset': offset
        }

        response = requests.get('https://api.spotify.com/v1/me/playlists', params=params, headers=headers)

        response_json = response.json()

        if(response.status_code == 200):
            return response_json['items']
        else:
            if response_json['error']['status'] == 401:
                Spotify.error_401()
            elif response_json['error']['status'] == 403:
                Spotify.delete_oauth_file_and_restart()
            elif response_json['error']['status'] == 429:
                Spotify.exceeded_rate_limits()
            else:
                logging.error(response)
            return []



    def get_current_user_playlists(token : SpotifyTokenInfo, limit = 50, offset = 0) -> list:

        playlists_items = []

        headers = {
            "Authorization": "Bearer "+ token.access_token
        }

        params = '?limit=' + str(limit) + '&offset=' + str(offset)

        response = requests.get('https://api.spotify.com/v1/me/playlists' + params, headers=headers)

        response_json = response.json()

        

        if(response.status_code == 200):

            playlists_items.extend(response_json['items'])

            total_playlists = response_json['total']

            if total_playlists > 50:
                
                with ThreadPoolExecutor(max_workers=5) as executor:
                    offsets = [50 * num for num in range(1, (total_playlists // 50) + 1)]

                    fetch_playlists_with_args = partial(Spotify.fetch_playlists,token)

                    results = executor.map(fetch_playlists_with_args, offsets)

                    for result in results:
                        playlists_items.extend(result)

        else:
            if response_json['error']['status'] == 401:
                Spotify.error_401()
            elif response_json['error']['status'] == 403:
                Spotify.delete_oauth_file_and_restart()
            elif response_json['error']['status'] == 429:
                Spotify.exceeded_rate_limits()
            else:
                logging.error(response)
                
                
        return playlists_items
                
        
    def search_playlist_by_name(token : SpotifyTokenInfo, playlist_name : str):
        
        print('Obteniendo playlists de Spotify\n')
        before = time.time()
        playlists : list[Playlist] = Spotify.get_current_user_playlists(token)
        
        after = time.time()
        
        logging.debug('Spotify.search_playlist_by_name -> '+str(after-before)+'ms')
        
        found = False
        
        for playlist in playlists:
            if(playlist['name'] == playlist_name):
                print('Playlist encontrada, obteniendo canciones\n')
                return False, playlist
        
        
        print('No se ha encontrado la playlist con ese nombre.')
        return True, None
        
        
        
        # root = Playlist.from_dict(playlist[0])



    def fetch_tracks(token,user_country,playlist_href,offset):
        headers = {
            "Authorization": "Bearer " + token.access_token
        }
        params = {
            'market': user_country,
            'fields': 'total,items(track(name,id,artists(name)))',
            'limit': 50,
            'offset': offset
        }
        before = time.time()
        response = requests.get(playlist_href + '/tracks', params=params, headers=headers)
        response_json = response.json()
        after = time.time()
        logging.debug('Spotify.get_tracks_from_playlist_href -> ' + str(after - before) + 'ms')
        if response.status_code == 200:
            return response_json['items']
        else:
            if response_json['error']['status'] == 401:
                Spotify.error_401()
            elif response_json['error']['status'] == 403:
                Spotify.delete_oauth_file_and_restart()
            elif response_json['error']['status'] == 429:
                Spotify.exceeded_rate_limits()
            else:
                logging.error(response)
            return []
    
    

    def async_get_tracks_from_playlist_href(token : SpotifyTokenInfo, playlist_href : str):
        playlists_tracks = []

        user_id, user_country = Spotify.get_user_info(token)
        
        headers = {
            "Authorization": "Bearer "+ token.access_token
        }
        
        params = {
            'market': user_country,
            'fields': 'total,items(track(name,id,artists(name)))',
            'limit': 50,
            'offset': 0
        }
        
        before = time.time()

        response = requests.get(playlist_href + '/tracks', params = params, headers=headers)
        
        response_json = response.json()
        
        after = time.time()
        
        logging.debug('Spotify.get_tracks_from_playlist_href -> '+str(after-before)+'ms')
        
        if(response.status_code == 200):

            playlists_tracks.extend(response_json['items'])

            total_playlist_tracks = response_json['total']

            if total_playlist_tracks > 50:

                with ThreadPoolExecutor(max_workers=5) as executor:
                    offsets = [50 * num for num in range(1, (total_playlist_tracks // 50) + 1)]

                    fetch_tracks_with_args = partial(Spotify.fetch_tracks,token,user_country,playlist_href)

                    results = executor.map(fetch_tracks_with_args, offsets)

                    for result in results:
                        playlists_tracks.extend(result)

        else:
            if response_json['error']['status'] == 401:
                Spotify.error_401()
            elif response_json['error']['status'] == 403:
                Spotify.delete_oauth_file_and_restart()
            elif response_json['error']['status'] == 429:
                Spotify.exceeded_rate_limits()
            else:
                logging.error(response)
                return True, None
    
    
    
        formated = [item["track"] for item in playlists_tracks]  
        
        return False, formated



    def get_tracks_from_playlist_href(token : SpotifyTokenInfo, playlist_href : str):
    
        playlists_tracks = []

        user_id, user_country = Spotify.get_user_info(token)
        
        headers = {
            "Authorization": "Bearer "+ token.access_token
        }
        
        params = {
            'market': user_country,
            'fields': 'total,items(track(name,id,artists(name)))',
            'limit': 50,
            'offset': 0
        }
        
        before = time.time()

        response = requests.get(playlist_href + '/tracks', params = params, headers=headers)
        
        response_json = response.json()
        
        after = time.time()
        
        logging.debug('Spotify.get_tracks_from_playlist_href -> '+str(after-before)+'ms')
        
        if(response.status_code == 200):

            playlists_tracks.extend(response_json['items'])

            total_playlist_tracks = response_json['total']

            if total_playlist_tracks > 50:

                # TODO: Refactorizar el código para hacerlo recursivo o algo así
                
                for num in range(1,(total_playlist_tracks // 50) + 1):
                    headers = {
                        "Authorization": "Bearer "+ token.access_token
                    }
        
                    params = {
                        'market': user_country,
                        'fields': 'total,items(track(name,id,artists(name)))',
                        'limit': 50,
                        'offset': 50 * num
                    }
            
                    before = time.time()

                    response = requests.get(playlist_href + '/tracks', params = params, headers=headers)
                    
                    response_json = response.json()
                    
                    after = time.time()
                    
                    logging.debug('Spotify.get_tracks_from_playlist_href -> '+str(after-before)+'ms')

                    if(response.status_code == 200):
                        playlists_tracks.extend(response_json['items'])
                    else:
                        if response_json['error']['status'] == 401:
                            Spotify.error_401()
                        elif response_json['error']['status'] == 403:
                            Spotify.delete_oauth_file_and_restart()
                        else:
                            Spotify.exceeded_rate_limits()

        else:
            if response_json['error']['status'] == 401:
                Spotify.error_401()
            elif response_json['error']['status'] == 403:
                Spotify.delete_oauth_file_and_restart()
            elif response_json['error']['status'] == 429:
                Spotify.exceeded_rate_limits()
            else:
                logging.error(response)
    
    
    
        formated = [item["track"] for item in playlists_tracks]  
        
        return formated
    
    
    
    
    def from_track_to_string(tracks : list) -> list[str]:
        
        result_string_array = []
                    
        for track in tracks:
            try:
                res = track['name'] + ' - '
                
                first = True
                for artist in track['artists']:
                    if not first:
                        res += ', '
                    else:
                        first = False 
                    
                    res += artist['name']
                    
                result_string_array.append(res)
            except Exception as err:
                pass
        
        return result_string_array
    
    

    def get_tracks_from_playlist_with_name(token : SpotifyTokenInfo, playlist_name: str) -> list[str]:
        
        retry, playlist = Spotify.search_playlist_by_name(token,playlist_name)
        
        if retry:
            return True, None
        
        # 'https://api.spotify.com/v1/playlists/1YDlr9UmPQF4jFs357t5eS/tracks'

        before = time.time()
        retry, playlist_tracks = Spotify.async_get_tracks_from_playlist_href(token,playlist['href'])
        after = time.time()
        
        if retry:
            return True, None
        
        logging.debug('Spotify.get_tracks_from_playlist_with_name -> '+str(after-before)+'ms')

        
        playlist_tracks_string = Spotify.from_track_to_string(playlist_tracks)     
                
        return False, playlist_tracks_string
        
        
        
        
        



    
