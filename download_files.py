import os
import sys
import re
from ConfigParser import SafeConfigParser

from utils import check_create_folder, download_from_url
from process_kegg import KEGGSET_INFO_FOLDER

# Import and set logger
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def download_all_files(species_ini_file, base_download_folder,
                       secrets_location=None):
    """
    Reads config INI file for a species, which contains the files (and
    their locations, or URLs) that must be loaded for this species, and calls
    the download_from_url function for each of those files.

    Arguments:
    species_ini_file -- Path to the particular species INI file. This
    is a string.

    base_download_folder -- A string. Path of the root folder where download
    folders for other species will be created and where common downloaded files
    will be saved. This is stored in the main configuration INI file.

    secrets_location -- Optional string of location of the secrets INI
    file.

    Returns:
    Nothing, just downloads and saves files to download_folder

    """
    check_create_folder(base_download_folder)

    species_file = SafeConfigParser()
    species_file.read(species_ini_file)

    sd_folder = species_file.get('species_info', 'SPECIES_DOWNLOAD_FOLDER')
    check_create_folder(sd_folder)

    if species_file.has_section('GO'):
        if species_file.getboolean('GO', 'DOWNLOAD'):

            obo_url = species_file.get('GO', 'GO_OBO_URL')
            download_from_url(obo_url, base_download_folder)

            go_dir = os.path.join(sd_folder, 'GO')
            check_create_folder(go_dir)

            goa_urls = species_file.get('GO', 'ASSOC_FILE_URLS')
            goa_urls = re.sub(r'\s', '', goa_urls).split(',')

            for goa_url in goa_urls:
                download_from_url(goa_url, go_dir)

    if species_file.has_section('KEGG'):
        if species_file.getboolean('KEGG', 'DOWNLOAD'):

            kegg_root_url = species_file.get('KEGG', 'KEGG_ROOT_URL')

            kegg_info_url = kegg_root_url + species_file.get('KEGG',
                                                             'DB_INFO_URL')

            download_from_url(kegg_info_url, base_download_folder,
                              'kegg_db_info')

            kegg_dir = os.path.join(sd_folder, 'KEGG')
            check_create_folder(kegg_dir)

            ks_urls = species_file.get('KEGG', 'SETS_TO_DOWNLOAD')
            kegg_urls = [kegg_root_url + url.strip() for url in
                         ks_urls.split(',')]

            for kegg_url in kegg_urls:
                download_from_url(kegg_url, kegg_dir)

    if species_file.has_section('DO'):
        if species_file.getboolean('DO', 'DOWNLOAD'):
            do_dir = os.path.join(sd_folder, 'DO')
            check_create_folder(do_dir)

            obo_url = species_file.get('DO', 'DO_OBO_URL')
            download_from_url(obo_url, do_dir)

            mim2gene_url = species_file.get('DO', 'MIM2GENE_URL')
            download_from_url(mim2gene_url, do_dir)

            # The genemap_file needs a special Secret Key, which must be
            # retrieved from the secrets file if the user wishes to download
            # the genemap_file
            genemap_url = species_file.get('DO', 'GENEMAP_URL')

            if not secrets_location:
                logger.error('Secrets file was not passed to '
                             'download_all_files() function. A secrets file '
                             'containing an OMIM API secret key is required to'
                             ' download the genemap file to process Disease '
                             'Ontology.')
                sys.exit(1)

            secrets_file = SafeConfigParser()
            secrets_file.read(secrets_location)

            if not secrets_file.has_section('OMIM API secrets'):
                logger.error('Secrets file has no "OMIM API secrets" section,'
                             'which is required to download the genemap file '
                             ' to process Disease Ontology.')
                sys.exit(1)

            omim_secret_key = secrets_file.get('OMIM API secrets',
                                               'SECRET_KEY')
            genemap_url = genemap_url.replace('<SecretKey>', omim_secret_key)

            download_from_url(genemap_url, do_dir)


def download_kegg_info_files(kegg_set_ids, species_ini_file):
    """
    This is a KEGG-specific function that downloads the files containing
    information about the KEGG sets, such as their title, abstract, supporting
    publications, etc.

    Arguments:
    kegg_set_ids -- List of kegg set identifiers (e.g. hsa00010) for which
    info files will be downloaded.

    species_ini_file -- Path to the species INI config file. This
    is a string.

    Returns:
    Nothing, just downloads and saves files to keggset_info folder, which will
    be the SPECIES_DOWNLOAD_FOLDER + 'KEGG/keggset_info_folder'

    """
    species_file = SafeConfigParser()
    species_file.read(species_ini_file)

    sd_folder = species_file.get('species_info', 'SPECIES_DOWNLOAD_FOLDER')

    keggset_info_folder = os.path.join(sd_folder, KEGGSET_INFO_FOLDER)
    check_create_folder(keggset_info_folder)

    full_info_url = species_file.get('KEGG', 'KEGG_ROOT_URL') + \
        species_file.get('KEGG', 'SET_INFO_DIR')

    for kegg_id in kegg_set_ids:
        kegg_info_file = full_info_url + kegg_id
        download_from_url(kegg_info_file, keggset_info_folder)
