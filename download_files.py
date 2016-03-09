from ConfigParser import SafeConfigParser
import os
import tempfile
import shutil
import requests

# Import and set logger
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def download_from_url(url, download_folder):
    """
    In case the downloading process gets interrupted, a dummy tempfile is
    created in the download_folder for every file that is being downloaded.
    This tempfile is then erased once the file finishes downloading.

    Arguments:
    url -- The URL string where the annotation file must be downloaded from.

    download_folder -- Path of folder where annotation file from URL will
    be downloaded to. This is a string.

    Returns:
    True if file did not already exist and was able to be downloaded.
    Otherwise, return False.

    """

    filename = url.split('/')[-1]
    target_filename = download_folder + '/' + filename

    if os.path.exists(target_filename):
        logger.error('Not downloading file ' + filename + ', as it already'
                     ' exists in the download_folder specified.')
        return False

    try:
        temp = tempfile.NamedTemporaryFile(prefix=filename + '.',
                                           dir=download_folder)

        download_request = requests.get(url, stream=True)

        # chunk_size is in bytes
        for chunk in download_request.iter_content(chunk_size=4096):
            if chunk:
                temp.write(chunk)
                temp.flush()

        # Go back to the beginning of the tempfile and copy it to target folder
        temp.seek(0)
        target_fh = open(target_filename, 'w+b')
        shutil.copyfileobj(temp, target_fh)
        temp.close()  # This erases the tempfile
        return True

    except:
        logger.error('There was an error when downloading the file "' +
                     filename + '" - downloading could not be completed.')
        return False


def download_all_files(species_ini_file, download_folder):
    """
    Reads config INI file for a species, which contains the files (and
    their locations, or URLs) that must be loaded for this species.

    Arguments:
    species_ini_file -- Path to the particular species INI file. This
    is a string.

    download_folder -- Path of folder where annotations files will be
    downloaded to. This is a string.

    Returns:
    Nothing, just downloads and saves files to download_folder

    """

    species_file = SafeConfigParser()
    species_file.read(species_ini_file)

    if species_file.has_section('GO'):
        go_dir = download_folder + '/GO'

        if not os.path.exists(go_dir):
            os.mkdir(go_dir)
            logger.info('GO folder created.')
        else:
            logger.info('Folder ' + go_dir + ' already exists. ' +
                        'Saving downloaded files to this folder.')

        obo_file = species_file.get('GO', 'GO_OBO_FILE')
        goa_file = species_file.get('GO', 'ASSOCIATION_FILE')

        download_from_url(obo_file, go_dir)
        download_from_url(goa_file, go_dir)

    if species_file.has_section('KEGG'):
        kegg_dir = download_folder + '/KEGG'

        if not os.path.exists(kegg_dir):
            os.mkdir(kegg_dir)
            logger.info('KEGG folder created.')
        else:
            logger.info('Folder ' + kegg_dir + ' already exists. ' +
                        'Saving downloaded files to this folder.')

        kegg_root_url = species_file.get('KEGG', 'KEGG_ROOT_URL')

        all_urls = [kegg_root_url + x.strip() for x in species_file.get(
                'KEGG', 'SETS_TO_DOWNLOAD').split(',')]

        for kegg_set_url in all_urls:
            download_from_url(kegg_set_url, kegg_dir)

    if species_file.has_section('DO'):
        do_dir = download_folder + '/DO'

        if not os.path.exists(do_dir):
            os.mkdir(do_dir)
            logger.info('DO folder created.')
        else:
            logger.info('Folder ' + do_dir + ' already exists. ' +
                        'Saving downloaded files to this folder.')
        obo_file = species_file.get('DO', 'DO_OBO_FILE')
        download_from_url(obo_file, do_dir)


def download_kegg_info_files(species_ini_file, kegg_sets, download_folder):
    """

    """
    species_file = SafeConfigParser()
    species_file.read(species_ini_file)

    if not species_file.has_section('KEGG'):
        logger.error('Species INI file has no KEGG section. KEGG URLs are '
                     'needed to download information files for KEGG sets.')
        sys.exit(1)

    full_info_url = species_file.get('KEGG', 'KEGG_ROOT_URL') + \
        species_file.get('KEGG', 'SET_INFO_URL')

    for kegg_set in kegg_sets:
        kegg_info_file = full_info_url + kegg_set
        download_from_url(kegg_info_file, download_folder)
