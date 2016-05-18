import os
import tempfile
import shutil
import requests
import urllib
from urlparse import urlsplit

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def check_create_folder(folder_name):
    """
    Small utility function to check if a folder already exists, and
    create it if it doesn't.
    """
    logger.info('Creating folder ' + folder_name + '...')

    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
        logger.info(folder_name + ' folder created.')
    else:
        logger.info('Folder ' + folder_name + ' already exists. ' +
                    'Saving downloaded files to this folder.')


def download_from_url(url, download_folder, file_name=None):
    """
    In case the downloading process gets interrupted, a dummy tempfile is
    created in the download_folder for every file that is being downloaded.
    This tempfile is then erased once the file finishes downloading.

    Arguments:
    url -- The URL string where the annotation file must be downloaded from.

    download_folder -- Path of folder where annotation file from URL will
    be downloaded to. This is a string.

    file_name -- Optional string argument for the name the downloaded file will
    will have in download_folder. If this is None, it will be assigned the last
    part of the url.

    Returns:
    True if file did not already exist and was able to be downloaded.
    Otherwise, return False.

    """
    if file_name:
        filename = file_name
    else:
        filename = os.path.basename(urlsplit(url).path)

    target_filename = os.path.join(download_folder, filename)

    if os.path.exists(target_filename):
        logger.warning('Not downloading file ' + filename + ', as it already'
                       ' exists in the download_folder specified.')
        return False

    try:
        if url.startswith('ftp'):
            urllib.urlretrieve(url, target_filename)
            return True

        else:
            temp = tempfile.NamedTemporaryFile(prefix=filename + '.',
                                               dir=download_folder)

            download_request = requests.get(url, stream=True)

            # chunk_size is in bytes
            for chunk in download_request.iter_content(chunk_size=4096):
                if chunk:
                    temp.write(chunk)
                    temp.flush()

            # Go back to the beginning of the tempfile and copy it to
            # target folder
            temp.seek(0)
            target_fh = open(target_filename, 'w+b')
            shutil.copyfileobj(temp, target_fh)
            temp.close()  # This erases the tempfile
            return True

    except:
        logger.error('There was an error when downloading the file "' +
                     filename + '" - downloading could not be completed.')
        return False


def translate_gene_ids(tribe_url, gene_list, from_id, to_id):
    payload = {'gene_list': gene_list, 'from_id': from_id, 'to_id': to_id}
    response = requests.post(tribe_url + '/api/v1/gene/xrid_translate',
                             data=payload)
    return response


def build_tags_dictionary(tag_mapping_file, geneset_id_column,
                          geneset_name_column, tag_column, header):

    tags_dict = {}
    tag_file_fh = open(tag_mapping_file, 'r')

    if header:
        tag_file_fh.next()

    for line in tag_file_fh:
        toks = line.strip().split('\t')
        gs_id = toks[geneset_id_column]
        gs_name = toks[geneset_name_column]
        # Underscores may be used in files in place of spaces
        gs_name = gs_name.replace('_', ' ')
        gs_tag = toks[tag_column]

        if gs_id not in tags_dict:
            tags_dict[gs_id] = {'gs_name': gs_name, 'gs_tags': [gs_tag]}
        else:
            tags_dict[gs_id]['gs_tags'].append(gs_tag)

    tag_file_fh.close()
    return tags_dict
