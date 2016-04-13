import os
import sys
import argparse

from download_files import download_all_files
from process_kegg import process_kegg_sets
from process_go import process_go_terms
from process_do import process_do_terms
from utils import check_create_folder

# Import and set logger
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


if __name__ == "__main__":

    # Logging level can be input as an argument to logging.basicConfig()
    # function to get more logging output (e.g. level=logging.INFO)
    # The default level is logging.WARNING
    logging.basicConfig()

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

    if not os.path.isfile(ini_file_path):
        logger.error('Species INI file not found in this path: ' +
                     ini_file_path)
        sys.exit(1)

    logger.info('Creating download folder ' + download_folder + '...')
    check_create_folder(download_folder)

    download_all_files(ini_file_path, download_folder)
    process_kegg_sets(ini_file_path, download_folder + '/KEGG')
    process_go_terms(ini_file_path)
    process_do_terms(ini_file_path)
