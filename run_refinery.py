import os
import sys
import argparse

from download_files import download_all_files

# Import and set logger
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Package to download and process knowledge in annotations '
        'databases and convert to JSON.')

    parser.add_argument(
        '-i', '--INI_file', required=True, dest='ini_file_path',
        help='INI config file with locations of desired files.')

    parser.add_argument(
        '-d', '--download_folder', required=True, dest='download_folder',
        help='Folder where all annotations files will be downloaded to '
        '(absolute or relative path).')

    args = parser.parse_args()
    ini_file_path = args.ini_file_path
    download_folder = args.download_folder

    if not os.path.exists(ini_file_path):
        logger.error('Species INI file not found in this path: ' +
                     ini_file_path)
        sys.exit(1)

    logger.info('Creating download folder ' + download_folder)

    try:
        os.mkdir(download_folder)
    except OSError:
        logger.info('Folder ' + download_folder + ' already exists. ' +
                    'Saving downloaded files to this folder.')

    download_all_files(ini_file_path, download_folder)
