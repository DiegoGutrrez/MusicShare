import logging
# TODO: Comprobar el tamaño del archivo de logs

logging.basicConfig(level=logging.DEBUG, filename='musicshare.log', format='%(asctime)s - %(levelname)s - %(message)s')

# logging.getLogger("requests").setLevel(logging.WARNING)

logging.getLogger("urllib3").setLevel(logging.WARNING)