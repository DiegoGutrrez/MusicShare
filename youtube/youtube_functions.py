

import os

from model.config import YOUTUBE_TOKEN_PATH


class Youtube:
    def check_for_youtube_token_file():

        if os.path.exists(YOUTUBE_TOKEN_PATH):
            print(f"El archivo '{YOUTUBE_TOKEN_PATH}' existe.")

            return 0
        else:
            print(f"El archivo '{YOUTUBE_TOKEN_PATH}' no existe.")

            return -1
        
