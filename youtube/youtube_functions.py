

import os
from ytmusicapi import YTMusic

from model.config import YOUTUBE_TOKEN_PATH


class Youtube:
    def check_for_youtube_token_file():

        if os.path.exists(YOUTUBE_TOKEN_PATH):
            print(f"El archivo '{YOUTUBE_TOKEN_PATH}' existe.")

            return 0
        else:
            print(f"El archivo '{YOUTUBE_TOKEN_PATH}' no existe.")

            return -1
        


    def get_tracks_from_playlist(ytmusic : YTMusic, playlist_name : str) -> tuple[bool, list[str]]:

        playlists = ytmusic.get_library_playlists()

        # Busca la playlist con el nombre 'hola'
        playlist_id = None
        for playlist in playlists:
            if playlist['title'] == playlist_name:
                playlist_id = playlist['playlistId']
                break



        # Verifica si se encontró la playlist
        if playlist_id:
            # Obtiene las canciones de la playlist
            playlist_info = ytmusic.get_playlist(playlist_id, limit=None)  # Se puede ajustar el límite según sea necesario
            songs = playlist_info['tracks']
            

            retrieved_songs = []

            # Imprime la información de las canciones
            for song in songs:
                retrieved_songs.append(song['title'] + ' - ' + song['artists'][0]['name'])
                print(song['title'], '-', song['artists'][0]['name']) 
            print()

            return True, retrieved_songs

        else:
            print(f"No se encontró la playlist '{playlist_name}'")

            return False, None

