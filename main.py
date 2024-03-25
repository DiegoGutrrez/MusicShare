
from youtube.youtube_functions import Youtube


# try:
import json
# from ytmusicapi_local.main_ytmusicapi import obtain_ytmusic_access
from ytmusicapi_local.main_ytmusicapi import obtain_ytmusic_access
from ytmusicapi_local.ytmusic import YTMusic
from spotify.spotify_functions import *
from local_web_server import *
import spotify.spotify_functions as spotify_functions

from urllib.parse import urlencode, urljoin, urlparse, urlunparse
import sys
import webbrowser

spotify_token_info : SpotifyTokenInfo
ytmusic: YTMusic = None

def playlist_ytmusic_to_spotify():

    global ytmusic
    global spotify_token_info

    retry = True

    ytmusic_playlist_name = ''
    spotify_playlist_name = ''


    while retry:
        
        while ytmusic_playlist_name == '':
            ytmusic_playlist_name = input('\nIntroduce el nombre de la playlist de Youtube Music: ')

        while spotify_playlist_name == '':
            spotify_playlist_name = input('\nIntroduce el nombre de la playlist a crear en Spotify: ')

        print()

        tracks = []
        
        print('Obteniendo canciones de la lista...\n')
        res_bool, tracks = Youtube.get_tracks_from_playlist(ytmusic,ytmusic_playlist_name)

        if res_bool == False:
            continue

        if(len(tracks) > 100):
            tracks_sublists = []

            for i in range(0, len(tracks), 100):
                tracks_sublist = tracks[i:i+100]
                tracks_sublists.append(tracks_sublist)


            playlist_id = Spotify.create_playlist_and_fill(spotify_token_info, spotify_playlist_name, tracks_sublists[0])
            

            user_id, user_country = Spotify.get_user_id(spotify_token_info)

            for num in range(1, len(tracks_sublists)):
                track_uris : list[str] = []

                for track in tracks_sublists[num]:
                    track_uri = Spotify.search_track(spotify_token_info, track, SearchType.track, user_country, 4)
                    if(track_uri != None):
                        track_uris.append(track_uri)

                Spotify.add_tracks_to_playlist(spotify_token_info,playlist_id,track_uris,None)

        else:
            Spotify.create_playlist_and_fill(spotify_token_info, spotify_playlist_name, tracks)

        
        retry = False
    return




def playlist_spotify_to_ytmusic():

    global ytmusic
    global spotify_token_info

    Spotify.get_current_user_playlists(spotify_token_info)

    return


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

Spotify.check_if_expired_token(spotify_token_info)

if(Youtube.check_for_youtube_token_file() == -1):
    obtain_ytmusic_access()
else:
    ytmusic = YTMusic(YOUTUBE_TOKEN_PATH)




read = input('\nSelecciones una opción (escriba el número y pulse ENTER)\n\n\t1) Playlist de Youtube Music a Spotify\n\t2) Playlist de Spotify a Youtube Music\n\n-> ')


if read.strip() == "1":
    playlist_ytmusic_to_spotify()    
elif read.strip() == "2":
    playlist_spotify_to_ytmusic()
else:
    print()


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

