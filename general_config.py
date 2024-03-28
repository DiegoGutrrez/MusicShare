import logging
from logging.handlers import RotatingFileHandler

# Configurar el logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Configurar un RotatingFileHandler
log_filename = 'musicshare.log'
max_log_size = 1024 * 1024  # 1 MB
backup_count = 1  # Número máximo de archivos de respaldo
file_handler = RotatingFileHandler(log_filename, maxBytes=max_log_size, backupCount=backup_count)
file_handler.setLevel(logging.DEBUG)

# Definir el formato del registro
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Agregar el manejador al logger
logger.addHandler(file_handler)

# Configurar el logging para las librerías urllib3 y requests
logging.getLogger("urllib3").setLevel(logging.WARNING)