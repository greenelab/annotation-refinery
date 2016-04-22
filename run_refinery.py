import os
import sys
import argparse
from ConfigParser import SafeConfigParser

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
    logging.basicConfig()  # )level=logging.INFO)

    parser = argparse.ArgumentParser(
        description='Package to download and process knowledge in annotations '
        'databases, convert to JSON, and save to Tribe webserver if desired.')

    parser.add_argument(
        '-i', '--INI_file', required=True, dest='ini_file_path',
        help='INI config file with locations of desired files.')

    args = parser.parse_args()
    ini_file_path = args.ini_file_path

    if not os.path.isfile(ini_file_path):
        logger.error('Species INI file not found in this path: ' +
                     ini_file_path)
        sys.exit(1)

    species_file = SafeConfigParser()
    species_file.read(ini_file_path)

    if not species_file.has_option('download_folder', 'BASE_DOWNLOAD_FOLDER'):
        logger.error('Species INI file must have a "download_folder" section, '
                     'which must contain a "BASE_DOWNLOAD_FOLDER" parameter'
                     ' where download folders will be created for each type'
                     ' of annotation.')
        sys.exit(1)

    download_folder = species_file.get('download_folder', 'BASE_DOWNLOAD_FOLDER')
    check_create_folder(download_folder)

    download_all_files(ini_file_path)

    all_kegg_sets = process_kegg_sets(ini_file_path)
    all_go_terms = process_go_terms(ini_file_path)
    all_do_terms = process_do_terms(ini_file_path)
