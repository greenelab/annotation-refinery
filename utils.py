import os

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def check_create_folder(folder_name):
    """
    Small utility function to check if a folder already exists, and
    create it if it doesn't.
    """
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
        logger.info(folder_name + ' folder created.')
    else:
        logger.info('Folder ' + folder_name + ' already exists. ' +
                    'Saving downloaded files to this folder.')
