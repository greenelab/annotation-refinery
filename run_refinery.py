import os
import sys
import argparse
from ConfigParser import SafeConfigParser

from download_files import download_all_files
from process_kegg import process_kegg_sets
from process_go import process_go_terms
from process_do import process_do_terms
from utils import check_create_folder
from loader import load_to_tribe

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
        'databases, convert to JSON, and save to Tribe webserver if desired.')

    parser.add_argument(
        '-i', '--INI_file', required=True, dest='ini_file_path',
        help='Main INI configuration file containing settings to run refinery.'
        ' Please consult our README for additional documentation.')

    args = parser.parse_args()
    ini_file_path = args.ini_file_path

    if not os.path.isfile(ini_file_path):
        logger.error('Main INI configuration file not found in this path: ' +
                     ini_file_path)
        sys.exit(1)

    main_config_file = SafeConfigParser()
    main_config_file.read(ini_file_path)

    if not main_config_file.has_option('download_folder',
                                       'BASE_DOWNLOAD_FOLDER'):
        logger.error('Main configuration file must have a "download_folder" '
                     'section, which must contain a "BASE_DOWNLOAD_FOLDER" '
                     'parameter where download folders will be created for '
                     'each type of annotation.')
        sys.exit(1)

    download_folder = main_config_file.get('download_folder',
                                           'BASE_DOWNLOAD_FOLDER')
    check_create_folder(download_folder)

    secrets_file = None
    if main_config_file.has_option('main', 'SECRETS_FILE'):
        secrets_file = main_config_file.get('main', 'SECRETS_FILE')

    process_to = main_config_file.get('main', 'PROCESS_TO')

    species_files = main_config_file.get('species files', 'SPECIES_FILES')

    # Make a list of the locations of all species files:
    species_files = species_files.replace(' ', '').split(',')

    for species_file in species_files:

        download_all_files(species_file, secrets_location=secrets_file)

        all_genesets = []

        if species_file.has_section('GO'):
            all_go_terms = process_go_terms(species_file)
            all_genesets.extend(all_go_terms)

        if species_file.has_section('KEGG'):
            all_kegg_sets = process_kegg_sets(species_file)
            all_genesets.extend(all_kegg_sets)

        if species_file.has_section('DO'):
            all_do_terms = process_do_terms(species_file)
            all_genesets.extend(all_do_terms)

        if process_to == 'Tribe':
            for geneset in all_genesets:
                load_to_tribe(ini_file_path, geneset)
