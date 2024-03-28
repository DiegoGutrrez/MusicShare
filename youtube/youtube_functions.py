

from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
import os
import threading
import time
from ytmusicapi_local.ytmusic import YTMusic, YTMusicBase
from general_config import logging
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

        print('Obteniendo playlists de Youtube Music\n')
        playlists = ytmusic.get_library_playlists()

        playlist_id = None
        for playlist in playlists:
            if playlist['title'] == playlist_name:
                playlist_id = playlist['playlistId']
                break


        if playlist_id:
            print('Playlist encontrada, obteniendo canciones\n')
            
            playlist_info = ytmusic.get_playlist(playlist_id, limit=None)
            songs = playlist_info['tracks']

            retrieved_songs = []

            print('Canciones recuperadas:\n')
            for song in songs:
                retrieved_songs.append(song['title'] + ' - ' + song['artists'][0]['name'])
                print(song['title'], '-', song['artists'][0]['name']) 
            print()

            return True, retrieved_songs

        else:
            print(f"No se encontró la playlist '{playlist_name}'")

            return False, None
        
        
        
    def search_video_id(ytmusic : YTMusic, track):
        
        res = ytmusic.search(track, 'songs', None, 5, True)
        try:
            return res[0]['videoId']
        except Exception as err:
            return None
        
        
    # def bucle(executor:ThreadPoolExecutor):
    #     while True:
    #         print(f"Hilos en ejecución: {executor._work_queue.qsize()}")
    #         # print(f"\rHilos en ejecución: {executor._work_queue.qsize()}", end="", flush=True)
    #         time.sleep(200 / 1000)
    
    def search_songs_by_name(ytmusic : YTMusic, tracks_to_add: list[str]):
        
        total_a_realizar = len(tracks_to_add)
        total_respuestas = 0
    
        def imprimir_progreso(total_respuestas, total_a_realizar):
            print(f"\r{total_respuestas}/{total_a_realizar}", end="", flush=True)
        
        
        tracks_ids = []
        before = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for track in tracks_to_add:
                future = executor.submit(Youtube.search_video_id, ytmusic, track)
                futures.append((track, future))

            for track, future in futures:
                result = future.result()
                tracks_ids.append(result)
                
                total_respuestas += 1
                imprimir_progreso(total_respuestas, total_a_realizar)
                
                    
        after = time.time()
        
        logging.debug('Youtube.create_playlist_and_fill_with_names -> '+str(after-before)+'ms')
        
        print("\rBúsqueda completada")
        
        print()
        return tracks_ids
    
    
        
    def create_playlist_and_fill_with_names(ytmusic : YTMusic, playlist_name: str ,tracks_to_add: list[str]):

        
        tracks_ids = Youtube.search_songs_by_name(ytmusic,tracks_to_add)
        
        res = ytmusic.create_playlist(playlist_name,'','PRIVATE',tracks_ids,None)
        
        print('Playlist creada con éxito\n')
        
            
        return tracks_ids