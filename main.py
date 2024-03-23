
from youtube.youtube_functions import Youtube


# try:
import json
# from ytmusicapi_local.main_ytmusicapi import obtain_ytmusic_access
from ytmusicapi_local.ytmusic import YTMusic
from spotify.spotify_functions import *
from local_web_server import *
import spotify.spotify_functions as spotify_functions

from urllib.parse import urlencode, urljoin, urlparse, urlunparse
import sys
import webbrowser

# obtain_ytmusic_access()
# sys.exit()

spotify_token_info : SpotifyTokenInfo


print('''   
            ___  ___          _      _____ _                                _____  __  
            |  \/  |         (_)    /  ___| |                              |  _  |/  | 
            | .  . |_   _ ___ _  ___\ `--.| |__   __ _ _ __ ___      __   _| |/' |`| | 
            | |\/| | | | / __| |/ __|`--. \ '_ \ / _` | '__/ _ \     \ \ / /  /| | | | 
            | |  | | |_| \__ \ | (__/\__/ / | | | (_| | | |  __/      \ V /\ |_/ /_| |_
            \_|  |_/\__,_|___/_|\___\____/|_| |_|\__,_|_|  \___|       \_/  \___(_)___/
        \n\n''')


# read = input(' Se necesita acceso a sus cuentas de Spotify y Google, si quiere continuar pulse  ENTER  ')

print()

# if read.strip() != "":
#     sys.exit()

spotify_token_info = Spotify.get_spotify_auth()


if(Youtube.check_for_youtube_token_file() == -1):
    ytmusic = YTMusic(YOUTUBE_TOKEN_PATH)




read = input('\nSelecciones una opción (escriba el número y pulse ENTER)\n\n\t1) Playlist de Youtube Music a Spotify\n\t2) Playlist de Spotify a Youtube Music\n\n-> ')


if read.strip() == "1":
     sys.exit()
elif read.strip() == "2":
    print()
else:
    print()




tracks = [
    "La Playa - La Oreja de Van Gogh",
    "Rosas - La Oreja de Van Gogh",
    "Muñeca de Trapo - La Oreja de Van Gogh",
    "Dulce Locura - La Oreja de Van Gogh",
    "Decode (Twilight Soundtrack Version) - Paramore",
    "Misery Business - Paramore",
    "Live Your Life (feat. Rihanna) - T.I.",
    "Ain't It Fun - Paramore"
]


Spotify.create_playlist_and_fill('Prueba Óscar UwU',tracks)

print("EY2")
input()

# Obtiene todas las playlists del usuario autenticado
playlists = ytmusic.get_library_playlists()

# Busca la playlist con el nombre 'hola'
playlist_id = None
for playlist in playlists:
    if playlist['title'] == 'Coche':
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
    print("No se encontró la playlist 'Coche'")

tracks = retrieved_songs




    








    #response = requests.get('https://api.spotify.com/v1/me/playlists', headers=headers)

# except Exception as err:
#     print("Error : ", err)
#     input()


sys.exit()



    # # Solicita al usuario que ingrese un entero
    # entrada = input("\n\n1) Spotify to YT music\n2)YT music to Spotify\n ")

    # # Convierte la entrada en un entero
    # try:
    #     numero_entero = int(entrada)
    #     print("El número ingresado es:", numero_entero)
    # except ValueError:
    #     print("La entrada no es un número entero válido.")


    # ytmusic = YTMusic("oauth.json")


    # # Obtiene todas las playlists del usuario autenticado
    # playlists = ytmusic.get_library_playlists()

    # # Busca la playlist con el nombre 'hola'
    # playlist_id = None
    # for playlist in playlists:
    #     if playlist['title'] == 'Clásicos general':
    #         playlist_id = playlist['playlistId']
    #         break



    # # Verifica si se encontró la playlist
    # if playlist_id:
    #     # Obtiene las canciones de la playlist
    #     playlist_info = ytmusic.get_playlist(playlist_id, limit=100)  # Se puede ajustar el límite según sea necesario
    #     songs = playlist_info['tracks']
        

    #     retrieved_songs = []

    #     # Imprime la información de las canciones
    #     for song in songs:
    #         retrieved_songs.append(song['title'] + ' - ' + song['artists'][0]['name'])
    #         print(song['title'], '-', song['artists'][0]['name'])  # Imprime el título y el nombre del artista de cada canción
    #     print()
    # else:
    #     print("No se encontró la playlist 'Clásicos general'")

