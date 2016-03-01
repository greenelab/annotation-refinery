from os.path import normpath
import sys
import argparse
from ConfigParser import SafeConfigParser
import requests


def download_from_url(url, download_folder):
    """
    In case the downloading process gets interrupted, a dummy tempfile is
    created in the target_folder for every file that is being downloaded.
    This tempfile is then erased once the file finishes downloading. This
    way the user will know what zip file did not finish downloading and
    can then erase the portion of it that has been saved so that the
    whole file can be downloaded again.
    """

    filename = url.split('/')[-1]
    target_filename = download_folder + '/' + filename
    temp = tempfile.NamedTemporaryFile(prefix=filename + '.',
                                       dir=target_folder)

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


def download_all_files(species_ini_file, download_folder):
    """
    """

    species_file = SafeConfigParser()
    species_file.read(species_ini_file)

    if species_file.has_section('GO'):

        obo_file = species_file.get('GO', 'GO_OBO_FILE')
        goa_file = species_file.get('GO', 'ASSOCIATION_FILE')

        download_from_url(obo_file, download_folder)
        download_from_url(goa_file, download_folder)

    if species_file.has_section('KEGG'):

        kegg_root_url = species_file.get('KEGG', 'KEGG_ROOT_URL')
        all_urls = [kegg_root_url + x.strip() for x in species_file.get(
                'KEGG', 'SETS_TO_DOWNLOAD').split(',')]

        for kegg_set in all_urls:
            download_from_url(kegg_set, download_folder)
