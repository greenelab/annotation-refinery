import os
import sys
from collections import defaultdict
from ConfigParser import SafeConfigParser

from slugify import slugify
from utils import build_tags_dictionary

# Import and set logger
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

KEGGSET_INFO_FOLDER = 'KEGG/keggset_info_folder'


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

        if toks[0].split(':')[0] == 'md':
            # Modules are prefixed with species and underscore
            group = group.split('_').pop()

        geneid = toks[1].split(':')[1]  # gene listed second, has prefix
        kegg_set_members[group].add(geneid)

    return kegg_set_members


def get_kegg_set_info(kegg_set_info_file, org_slug):
    """
    Function to read in kegg_set_info_file and make a dictionary of the KEGG
    set with the information in this file.

    Arguments:
    kegg_set_info_file -- Path to file of information for specific KEGG
    set. This is a string.

    org_slug -- A string of the organism's scientific name, modified
    so that all characters are lowercase and whitespace is replaced
    with a hyphen. This is done with the slugify.slugify() function.

    Returns:
    set_info_dict -- Dictionary with 'title' and 'abstract' (which correspond
    to 'NAME' and 'DESCRIPTION' respectively in kegg_set_info_file) for a
    specific KEGG set.

    """
    kegg_set_info_fh = open(kegg_set_info_file, 'r')
    set_info_dict = {}

    kegg_set_type = None
    ks_title = None

    for line in kegg_set_info_fh:
        if line.startswith('ENTRY'):
            toks = line.split()
            set_info_dict['kegg_id'] = toks[1]
            kegg_set_type = toks[-1]
        if line.startswith('NAME'):
            ks_title = ' '.join(line.split()[1:])
        if line.startswith('DESCRIPTION'):
            set_info_dict['abstract'] = ' '.join(line.split()[1:])

    if ks_title:
        # Make KEGG set title more search-friendly
        set_info_dict['title'] = 'KEGG-' + kegg_set_type + '-' + \
            set_info_dict['kegg_id'] + ': ' + ks_title

        # Add org_slug to the geneset 'slug'
        set_info_dict['slug'] = org_slug + '-' + \
            set_info_dict['kegg_id'].lower()

        if 'abstract' not in set_info_dict:
            set_info_dict['abstract'] = ''
    return set_info_dict


def build_kegg_sets(kegg_sets_members, keggset_info_folder, organism, xrdb,
                    tags_dictionary=None):
    """
    Function to build all KEGG sets **for a given set type** (e.g. pathway,
    module, disease, etc.), since members_file will only contain members
    for KEGG sets of a specific type.

    Arguments:
    kegg_sets_members -- This is a dictionary of each KEGG set ID as a key
    and the members in that set as the value.

    keggset_info_folder -- A string - folder where all KEGG set info files
    have been saved to. The files were saved to this folder by the
    download_kegg_info_files() function if running the full annotation-refinery

    organims -- A string of the scientific name for our desired organism
    (e.g. 'Homo sapiens').

    xrdb -- A string. The name of the cross-reference database (i.e. type of
    gene identifier) used by KEGG in the members file(s) for this species.

    tags_dictionary -- A dictionary of tags to be added to the KEGG sets,
    made by the utils.build_tags_dictionary() function

    Returns:
    all_kegg_sets -- A list of processed KEGG sets, where each KEGG set is
    a Python dictionary, containing its title, abstract, and annotations.

    """

    all_kegg_sets = []

    for kegg_id in kegg_sets_members.keys():
        info_file = os.path.join(keggset_info_folder, kegg_id)
        org_slug = slugify(organism)

        kegg_set_info = get_kegg_set_info(info_file, org_slug)

        kegg_set_info['organism'] = organism
        kegg_set_info['xrdb'] = xrdb
        kegg_set_info['annotations'] = {}

        # This following loop fills out annotations. Since KEGG sets do not
        # have publications associated with their genes, each gene will have
        # an empty list as a value in the set's annotations.
        for member in kegg_sets_members[kegg_id]:
            if xrdb == 'Entrez':
                try:
                    kegg_set_info['annotations'][int(member)] = []
                except ValueError:
                    logger.error('Entrez ID %s could not be coerced to an '
                                 'integer and was not included in KEGG set'
                                 'with kegg_id %s', member, kegg_id)
            else:
                kegg_set_info['annotations'][member] = []

        if tags_dictionary and kegg_id in tags_dictionary:
            kegg_set_info['tags'] = tags_dictionary[kegg_id]['gs_tags']

        all_kegg_sets.append(kegg_set_info)

    return all_kegg_sets


def process_kegg_sets(species_ini_file, base_download_folder):
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
    from download_files import download_kegg_info_files

    species_file = SafeConfigParser()
    species_file.read(species_ini_file)

    if not species_file.has_section('KEGG'):
        logger.error('Species INI file has no KEGG section, which is needed'
                     ' to run the process_kegg_terms function.')
        sys.exit(1)

    kegg_info_file = os.path.join(base_download_folder, 'kegg_db_info')
    kegg_db_info = get_kegg_info(kegg_info_file)
    logger.info('Working with KEGG release %s.', kegg_db_info['release'])
    logger.info('KEGG Database info: %s.', kegg_db_info)

    tags_dictionary = None
    if species_file.has_option('KEGG', 'TAG_MAPPING_FILE'):
        tag_mapping_file = species_file.get('KEGG', 'TAG_MAPPING_FILE')
        kegg_id_column = species_file.getint('KEGG', 'KEGG_ID_COLUMN')
        kegg_name_column = species_file.getint('KEGG', 'KEGG_NAME_COLUMN')
        tag_column = species_file.getint('KEGG', 'TAG_COLUMN')
        header = species_file.getboolean('KEGG', 'TAG_FILE_HEADER')

        tags_dictionary = build_tags_dictionary(tag_mapping_file,
                                                kegg_id_column,
                                                kegg_name_column, tag_column,
                                                header)

    organism = species_file.get('species_info', 'SCIENTIFIC_NAME')
    sd_folder = species_file.get('species_info', 'SPECIES_DOWNLOAD_FOLDER')

    xrdb = species_file.get('KEGG', 'XRDB')

    ks_urls = species_file.get('KEGG', 'SETS_TO_DOWNLOAD')
    kegg_types = [os.path.basename(url.strip()) for url in ks_urls.split(',')]

    keggset_info_folder = os.path.join(sd_folder, KEGGSET_INFO_FOLDER)

    all_kegg_sets = []
    for kegg_type in kegg_types:
        members_file = os.path.join(sd_folder, 'KEGG', kegg_type)
        kegg_sets_members = get_kegg_sets_members(members_file)
        download_kegg_info_files(kegg_sets_members.keys(), species_ini_file)
        kegg_sets = build_kegg_sets(kegg_sets_members, keggset_info_folder,
                                    organism, xrdb, tags_dictionary)
        all_kegg_sets.extend(kegg_sets)
    return all_kegg_sets
