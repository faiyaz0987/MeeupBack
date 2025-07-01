# import logging
# import os

# LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'db_setup', 'logs')
# os.makedirs(LOG_DIR, exist_ok=True)

# def get_logger(name):
#     logger = logging.getLogger(name)
#     if not logger.handlers:
#         logger.setLevel(logging.DEBUG)
#         file_handler = logging.FileHandler(os.path.join(LOG_DIR, f'{name}.log'))
#         formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
#         file_handler.setFormatter(formatter)
#         logger.addHandler(file_handler)
#     return logger


import logging
import os

LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'db_setup', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # File handler
        file_handler = logging.FileHandler(os.path.join(LOG_DIR, f'{name}.log'))
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger
