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
    version.

    Arguments:
    kegg_info_file --

    Returns:
    kegg_info_dict

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
    kegg_sets_file --

    Returns:
    kegg_set_members

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
    Function to read in kegg_info_file and make a dictionary of the KEGG
    set with all attributes in this file.

    Arguments:
    kegg_set_info_file --

    Returns:
    set_info_dict

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


def process_kegg_sets(species_ini_file, kegg_folder):
    """
    Function to put together the dictionaries output by get_kegg_sets_members
    and get_kegg_set_info to assemble KEGG sets.

    Arguments:
    set_info_dir --

    kegg_set_members --

    Returns:
    all_kegg_sets

    """
    species_file = SafeConfigParser()
    species_file.read(species_ini_file)

    if not species_file.has_section('KEGG'):
        logger.error('Species INI file has no KEGG section. KEGG sets were '
                     'not able to be processed.')
        sys.exit(1)

    all_kegg_sets = []

    for kegg_set_id, genes in kegg_set_members.iteritems():
        download_kegg_info_files()


    for info_file in glob.glob(set_info_dir + '/*'):
        kegg_set_info = get_kegg_set_info(info_file)
        kegg_set_id = kegg_set_info['kegg_id']
        kegg_set_info['genes'] = kegg_set_members[kegg_set_id]
        all_kegg_sets.append(kegg_set_info)

    return all_kegg_sets
