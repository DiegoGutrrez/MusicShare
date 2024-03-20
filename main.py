import json
from ytmusicapi import YTMusic
from spotify_functions import *
from local_web_server import *
import spotify_functions
import requests
import os
from urllib.parse import urlencode, urljoin, urlparse, urlunparse
import sys
import webbrowser


spotify_token_info : SpotifyAccessTokenInfo = get_spotify_auth()






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

