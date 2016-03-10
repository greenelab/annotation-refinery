import os
import glob
from collections import defaultdict

# Import and set logger
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_kegg_info(kegg_info_file):
    """
    Function to return a dictionary of the information for this KEGG
    database version.

    Arguments:
    kegg_info_file -- Path to file that contains KEGG database information.
    This file was downloaded by the download_all_files() function in
    download_files.py.

    Returns:
    kegg_info_dict -- Dictionary with all of the information in kegg_info_file.
    This includes the realease information (in the 'release' key), as well as
    the number of entries currently in the database for 'pathway', 'brite',
    'module', 'disease', 'drug', 'genes', among others.

    """
    kegg_info_fh = open(kegg_info_file, 'r')
    kegg_info_dict = {}

    title_line = kegg_info_fh.next()
    kegg_info_dict['title'] = title_line.strip().split('             ')[1]

    release_line = kegg_info_fh.next()
    release_info = release_line.strip().split('             ')[1]
    if release_info.startswith('Release'):
        kegg_info_dict['release'] = release_info
    else:
        kegg_info_dict['release'] = None

    kegg_info_dict['lab_info'] = kegg_info_fh.next().strip()

    for line in kegg_info_fh:
        toks = line.strip().split()
        kegg_info_dict[toks[0]] = ' '.join(toks[1:])

    kegg_info_fh.close()

    return kegg_info_dict


def get_kegg_sets_members(kegg_sets_file):
    """
    Reads in file with all the KEGG sets and associated members

    Arguments:
    kegg_sets_file -- Path to file that contains all of the KEGG sets and
    their members/genes for a specific type of sets (e.g. pathway,
    module, etc.). This file was downloaded by the download_all_files()
    function in download_files.py.

    Returns:
    kegg_set_members -- Dictionary containing all of the KEGG sets in
    the kegg_sets_file as keys, and a Python set of the members/genes
    they contain as the value.

    """
    kegg_sets_fh = open(kegg_sets_file, 'r')

    # TODO: Advantage of having a defaultdict here instead of
    # normal dictionary?
    kegg_set_members = defaultdict(set)

    for line in kegg_sets_fh:
        toks = line.strip().split()
        group = toks[0].split(':')[1]    # group listed first, has prefix
        geneid = toks[1].split(':')[1]  # gene listed second, has prefix
        kegg_set_members[group].add(geneid)

    return kegg_set_members


def get_kegg_set_info(kegg_set_info_file):
    """
    Function to read in kegg_set_info_file and make a dictionary of the KEGG
    set with the information in this file.

    Arguments:
    kegg_set_info_file -- Path to file of information for specific KEGG
    set. This is a string.

    Returns:
    set_info_dict -- Dictionary with 'title' and 'abstract' (which correspond
    to 'NAME' and 'DESCRIPTION' respectively in kegg_set_info_file) for a
    specific KEGG set.

    """
    kegg_set_info_fh = open(kegg_set_info_file, 'r')
    set_info_dict = {}

    for line in kegg_set_info_fh:
        if line.startswith('NAME'):
            set_info_dict['title'] = ' '.join(line.split()[1:])
        if line.startswith('DESCRIPTION'):
            set_info_dict['abstract'] = ' '.join(line.split()[1:])

    if 'title' in set_info_dict:
        if 'abstract' not in set_info_dict:
            set_info_dict['abstract'] = ''
    return set_info_dict


def process_kegg_sets(set_type, kegg_folder, species_ini_file):
    """
    Function to process all KEGG sets **for a given set_type** (e.g. pathway,
    module, disease, etc.).

    Arguments:
    set_type -- The type of KEGG sets which will be processed (e.g. 'pathway').
    This is a string, and it is also the name of the file containing all of
    the sets and the members/genes in those sets.

    kegg_folder -- Folder where all KEGG files are saved. This is the folder
    where the download_all_files() function downloaded the KEGG files
    to, and should be equal to <download_folder + '/KEGG'> if given a
    download_folder parameter when calling run_refinery.py.

    Returns:
    all_kegg_sets -- A list of processed KEGG sets, where each KEGG set is
    a Python dictionary with the required information as its keys and values.

    """

    kegg_db_info = get_kegg_info(kegg_folder + 'kegg_db_info')

    all_kegg_set_members = get_kegg_sets_members(kegg_folder + '/' + set_type)

    download_kegg_info_files(all_kegg_set_members.keys())

    all_kegg_sets = []

    for info_file in glob.glob(kegg_folder + '/*'):
        kegg_set_info = get_kegg_set_info(info_file)
        kegg_set_id = kegg_set_info['kegg_id']
        kegg_set_info['genes'] = kegg_set_members[kegg_set_id]
        all_kegg_sets.append(kegg_set_info)

    return all_kegg_sets
