from config import logger_filename
import logging


logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt='%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler = logging.FileHandler(logger_filename)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
