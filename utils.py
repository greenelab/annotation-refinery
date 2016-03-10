import os

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def check_create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
        logger.info(folder_name + ' folder created.')
    else:
        logger.info('Folder ' + folder_name + ' already exists. ' +
                    'Saving downloaded files to this folder.')
