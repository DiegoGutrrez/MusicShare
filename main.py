from ytmusicapi import YTMusic
from spotify_functions import *
from local_web_server import *
import spotify_functions
import requests
import os
from urllib.parse import urlencode, urljoin, urlparse, urlunparse
import sys
import webbrowser


spotify_url= 'https://accounts.spotify.com'
auth_url = '/authorize'
access_token_url = '/api/token'

# print('http://localhost:8888/callback')


code_verifier = Spotify.generate_random_string(64)
hashed = Spotify.sha256(code_verifier)
codeChallenge = Spotify.base64encode(hashed)


clientId = '076017c2352240a198382b8b4cec592f'
redirectUri = 'http://localhost:8888/callback'

scope = 'user-read-private user-read-email'

# Genera la URL de autorización de Spotify

params = {
    'response_type': 'code',
    'client_id': clientId,
    'scope': scope,
    'code_challenge_method': 'S256',
    'code_challenge': codeChallenge,
    'redirect_uri': redirectUri
}
auth_url_with_params = urljoin(spotify_url + auth_url, '?' + urlencode(params))

# Almacena el code_verifier en el almacenamiento local (si es necesario)
# Nota: en Python no hay un equivalente directo de window.localStorage, 
# así que aquí solo se está simulando el almacenamiento temporal
# os.environ['code_verifier'] = code_verifier

# Redirige al usuario a la URL de autorización de Spotify
webbrowser.open(auth_url_with_params)

authorization_code, state = StartWebServerUserAuth(8888)

spotify_access_token = Spotify.get_access_token_info(spotify_url + access_token_url, clientId, authorization_code, redirectUri, code_verifier)


sys.exit()
exit



# # Solicita al usuario que ingrese un entero
# entrada = input("\n\n1) Spotify to YT music\n2)YT music to Spotify\n ")

# # Convierte la entrada en un entero
# try:
#     numero_entero = int(entrada)
#     print("El número ingresado es:", numero_entero)
# except ValueError:
#     print("La entrada no es un número entero válido.")


ytmusic = YTMusic("oauth.json")


# Obtiene todas las playlists del usuario autenticado
playlists = ytmusic.get_library_playlists()

# Busca la playlist con el nombre 'hola'
playlist_id = None
for playlist in playlists:
    if playlist['title'] == 'Clásicos general':
        playlist_id = playlist['playlistId']
        break



# Verifica si se encontró la playlist
if playlist_id:
    # Obtiene las canciones de la playlist
    playlist_info = ytmusic.get_playlist(playlist_id, limit=100)  # Se puede ajustar el límite según sea necesario
    songs = playlist_info['tracks']
    

    retrieved_songs = []

    # Imprime la información de las canciones
    for song in songs:
        retrieved_songs.append(song['title'] + ' - ' + song['artists'][0]['name'])
        print(song['title'], '-', song['artists'][0]['name'])  # Imprime el título y el nombre del artista de cada canción
    print()
else:
    print("No se encontró la playlist 'Clásicos general'")

