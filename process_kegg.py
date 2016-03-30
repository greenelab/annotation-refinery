import os
import glob
from collections import defaultdict
from ConfigParser import SafeConfigParser
from download_files import download_kegg_info_files

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
        if line.startswith('ENTRY'):
            set_info_dict['kegg_id'] = line.split()[1]
        if line.startswith('NAME'):
            set_info_dict['title'] = ' '.join(line.split()[1:])
        if line.startswith('DESCRIPTION'):
            set_info_dict['abstract'] = ' '.join(line.split()[1:])

    if 'title' in set_info_dict:
        if 'abstract' not in set_info_dict:
            set_info_dict['abstract'] = ''
    return set_info_dict


def build_kegg_sets(kegg_sets_members, keggset_info_folder, organism):
    """
    Function to build all KEGG sets **for a given set type** (e.g. pathway,
    module, disease, etc.), since members_file will only contain members
    for KEGG sets of a specific type.

    Arguments:
    members_file -- This is a string, and is the name of the file containing
    all members in all KEGG sets for a specific type of KEGG set (e.g. pathway)

    keggset_info_folder -- A string - folder where all KEGG set info files
    have been saved to. The files were saved to this folder by the
    download_kegg_info_files() function if running the full annotation-refinery

    Returns:
    all_kegg_sets -- A list of processed KEGG sets, where each KEGG set is
    a Python dictionary, containing its title, abstract, and annotations.

    """

    all_kegg_sets = []

    for info_file in glob.glob(keggset_info_folder + '/*'):

        kegg_set_info = get_kegg_set_info(info_file)
        kegg_set_id = kegg_set_info['kegg_id']

        kegg_set_info['organism'] = organism
        kegg_set_info['annotations'] = set()

        for member in kegg_sets_members[kegg_set_id]:
            kegg_set_info['annotations'].add((member, None))

        all_kegg_sets.append(kegg_set_info)

    return all_kegg_sets


def process_kegg_sets(species_ini_file):
    """
    Function to process all KEGG sets using the build_kegg_sets()
    function above.

    Arguments:
    species_ini_file -- Path to the species INI config file. This
    is a string.

    Returns:
    all_kegg_sets -- A list of processed KEGG sets, where each KEGG set is
    a Python dictionary with the required information as its keys and values.

    """

    species_file = SafeConfigParser()
    species_file.read(species_ini_file)

    if not species_file.has_section('KEGG'):
        logger.error('Species INI file has no KEGG section, which is needed'
                     ' to run the process_kegg_terms function.')
        sys.exit(1)

    kegg_info_file = species_file.get('KEGG', 'KEGG_INFO_FILE')
    kegg_members_files = species_file.get('KEGG', 'KEGG_MEMBERS_FILES')
    keggset_info_folder = species_file.get('KEGG', 'KEGGSET_INFO_FOLDER')
    organism = species_file.get('species_info', 'SCIENTIFIC_NAME')

    kegg_db_info = get_kegg_info(kegg_info_file)

    all_kegg_sets = []
    for members_file in kegg_members_files.split(','):
        kegg_sets_members = get_kegg_sets_members(members_file)
        download_kegg_info_files(kegg_sets_members.keys(), species_ini_file)
        kegg_sets = build_kegg_sets(kegg_sets_members, keggset_info_folder,
                                    organism)
        all_kegg_sets.extend(kegg_sets)
    return all_kegg_sets
