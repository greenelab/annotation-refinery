import os
import re
import sys
import gzip
from urlparse import urlsplit
from ConfigParser import SafeConfigParser

from go import go
from slugify import slugify
from utils import build_tags_dictionary

# Import and set logger
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


GO_NAMESPACE_MAP = {
    'biological_process': 'BP',
    'molecular_function': 'MF',
    'cellular_component': 'CC',
}

DB_REMAP = {
    'FB': 'FLYBASE',
    'WB': 'WormBase',
}


def get_filtered_annotations(assoc_file, accepted_evcodes=None,
                             remove_leading_gene_id=None,
                             use_symbol=None, tax_id=None):
    """
    This function reads in the association file and returns a list of
    annotations. Only annotations that have evidence codes in
    'accepted_evcodes' (if accepted_evcodes is not None) and annotations
    that do not have details == 'NOT' will be included in this list.

    Arguments:
    assoc_file -- A string. Location of the GO association file to be
    read in.

    accepted_evcodes -- A list of evidence codes (e.g. ['EXP', 'IDA', 'IPI'])
    to filter the annotations by.

    remove_leading_gene_id -- True or False value. For some organisms, such
    as Mouse, there is a leading tag on the gene IDs column in the gene
    association file. This tag is just a duplicate of the type of gene
    identifier (already present in the identifier type (xrdb) column) and
    should be removed to get the pure gene ID (e.g. to get "99668" as
    opposed to "MGI:99668").

    Returns:
    annotations -- A list of all the annotations that meet the desired
    criteria. Each annotation in the list will be a tuple, which will
    contain: (<crossrefDB>, <crossrefID>, <goid>, <refstring>, <date>)
    """

    if assoc_file.endswith('.gz'):
        assoc_fh = gzip.open(assoc_file, 'r')
    else:
        assoc_fh = open(assoc_file, 'r')

    annotations = []

    for line in assoc_fh:
        if line.startswith('!'):
            continue

        toks = line.strip().split('\t')

        (xrdb, xrid, details, goid, refstring, ev_code, taxon, date) = (
            toks[0], toks[1], toks[3], toks[4], toks[5], toks[6],
            toks[12].split(':')[1], toks[13])

        if tax_id and (tax_id != taxon):
            continue

        if remove_leading_gene_id:
            xrid = xrid.split(':')[1]

        if xrdb in DB_REMAP:
            xrdb = DB_REMAP[xrdb]

        if use_symbol:
            xrdb = 'Symbol'
            if toks[0] == 'UniProtKB':
                xrid = toks[2]

        # These next few lines are needed for processing
        # Arabidopsis annotations
        if xrdb == 'TAIR':
            tair_regex = re.compile('AT[0-9MC]G[0-9][0-9][0-9][0-9][0-9]')
            first_alias = toks[10].split('|')[0]
            if tair_regex.match(toks[2]):
                xrid = toks[2]
            elif tair_regex.match(toks[9]):
                xrid = toks[9]
            elif tair_regex.match(first_alias):
                xrid = first_alias

        if details == 'NOT':
            continue

        if accepted_evcodes is not None and (ev_code not in accepted_evcodes):
            continue

        annotation = (xrdb, xrid, goid, refstring, date)

        annotations.append(annotation)

    return annotations


def create_go_term_title(go_term):
    """
    Small function to create the GO term title in the desired
    format: GO-<GO_NAMESPACE>-<GO integer ID>:<GO term full name>
    Example: GO-BP-0000280:nuclear division

    Arguments:
    go_term -- This is a go_term object from the go() class (go.go)

    Returns:
    title -- A string of the GO term's title in the desired format.
    """
    go_id = go_term.go_id.split(':')[1]

    namespace = GO_NAMESPACE_MAP[go_term.get_namespace()]

    title = 'GO' + '-' + namespace + '-' + go_id + ':' + go_term.full_name

    return title


def create_go_term_abstract(go_term, evlist=None):
    """
    Function to create the GO term abstract in the desired
    format.

    Arguments:
    go_term -- This is a go_term object from the go() class (go.go)

    evlist -- A list of evidence codes we will use to filter the annotations

    Returns:
    abstract -- A string of the GO term's abstract in the desired format.
    """
    evclause = ''
    if evlist is not None:

        evclause = ' Only annotations with evidence coded as '
        if len(evlist) == 1:
            evclause = evclause + evlist[0]
        else:
            evclause = evclause + ', '.join(evlist[:-1]) + ' or ' + evlist[-1]
        evclause = evclause + ' are included.'

    if go_term.description:
        description = go_term.description + ' Annotations are propagated ' + \
            'through transitive closure as recommended by the GO ' + \
            'Consortium.' + evclause
    else:
        logger.info("No description on term %s", go_term)
        # TODO: What do we put as description if go_term.description == None?

    return description


def process_go_terms(species_ini_file, base_download_folder):
    """
    Function to read in config INI file and run the other functions to
    process GO terms.
    """
    species_file = SafeConfigParser()
    species_file.read(species_ini_file)

    if not species_file.has_section('GO'):
        logger.error('Species INI file has no GO section, which is needed'
                     ' to run the process_go_terms function.')
        sys.exit(1)

    organism = species_file.get('species_info', 'SCIENTIFIC_NAME')
    sd_folder = species_file.get('species_info', 'SPECIES_DOWNLOAD_FOLDER')
    taxonomy_id = species_file.get('species_info', 'TAXONOMY_ID')

    obo_url = urlsplit(species_file.get('GO', 'GO_OBO_URL'))
    obo_filename = os.path.basename(obo_url.path)
    obo_file = os.path.join(base_download_folder, obo_filename)

    # Get whatever is saved in the ASSOC_FILE_URLS option minus any
    # whitespace characters.
    assoc_file_urls = re.sub(
        r'\s', '', species_file.get('GO', 'ASSOC_FILE_URLS'))

    # Convert this line into a list of urls, splitting by comma (','),
    # and then make a list with the filenames in each of these urls.
    assoc_file_url_list = [urlsplit(x) for x in assoc_file_urls.split(',')]
    assoc_filenames = [os.path.basename(x.path) for x in assoc_file_url_list]
    assoc_files = [os.path.join(sd_folder, 'GO', x) for x in assoc_filenames]

    evcodes = species_file.get('GO', 'EVIDENCE_CODES')
    evcodes = re.sub(r'\s', '', evcodes).split(',')

    use_symbol = None
    if species_file.has_option('GO', 'USE_SYMBOL'):
        use_symbol = species_file.getboolean('GO', 'USE_SYMBOL')

    remove_leading_gene_id = False
    if species_file.has_option('GO', 'REMOVE_LEADING_GENE_ID'):
        remove_leading_gene_id = species_file.getboolean(
            'GO', 'REMOVE_LEADING_GENE_ID')

    annotations = []
    for assoc_file in assoc_files:
        new_annotations = get_filtered_annotations(
            assoc_file, evcodes,
            remove_leading_gene_id=remove_leading_gene_id,
            use_symbol=use_symbol, tax_id=taxonomy_id)

        annotations.extend(new_annotations)

    gene_ontology = go()
    loaded_obo_bool = gene_ontology.load_obo(obo_file)
    if loaded_obo_bool is False:
        logger.error('GO OBO file could not be loaded.')

    for annotation in annotations:
        (xrdb, xrid, goid, refstring, date) = annotation

        refs = refstring.split('|')

        pub = None
        for ref in refs:
            # Check if publication source is PubMed (PMID).
            # Otherwise, keep pub as None.
            if ref.startswith('PMID:'):
                pub = ref.split(':')[1]

        gene_ontology.add_annotation(go_id=goid, gid=xrid, ref=pub,
                                     date=date, xdb=xrdb, direct=True)

    gene_ontology.populated = True
    gene_ontology.propagate()

    GO_terms = []

    tags_dictionary = None
    if species_file.has_option('GO', 'TAG_MAPPING_FILE'):
        tag_mapping_file = species_file.get('GO', 'TAG_MAPPING_FILE')
        go_id_column = species_file.getint('GO', 'GO_ID_COLUMN')
        go_name_column = species_file.getint('GO', 'GO_NAME_COLUMN')
        tag_column = species_file.getint('GO', 'TAG_COLUMN')
        header = species_file.getboolean('GO', 'TAG_FILE_HEADER')

        tags_dictionary = build_tags_dictionary(
            tag_mapping_file, go_id_column, go_name_column, tag_column, header)

    for (term_id, term) in gene_ontology.go_terms.iteritems():

        if not term.annotations:
            continue

        go_term = {}
        go_term['title'] = create_go_term_title(term)
        go_term['abstract'] = create_go_term_abstract(term, evcodes)
        go_term['organism'] = organism
        go_term['slug'] = slugify(term_id + '-' + organism)

        go_term['annotations'] = {}
        go_term_xrdb = None

        for annotation in term.annotations:
            if annotation.gid not in go_term['annotations']:
                # If annotation.gid is not already a key in the dictionary,
                # make it one and initialize list. Else, the key and list
                # already exist.
                go_term['annotations'][annotation.gid] = []

            if annotation.ref is not None:
                try:
                    go_term['annotations'][annotation.gid].append(
                        int(annotation.ref))
                except ValueError:
                    logger.error('Pubmed ID %s for GO term %s could not be '
                                 'converted to an integer.', annotation.ref,
                                 term_id)

            if annotation.xdb is not None:
                if go_term_xrdb and go_term_xrdb != annotation.xdb:
                    logger.info("There is more than one xrdb for annotations "
                                "in this GO term (%s and %s). Only the first "
                                "one will be saved in this GO term's 'xrdb' "
                                "field.", go_term_xrdb, annotation.xdb)
                else:
                    go_term_xrdb = annotation.xdb

        go_term['xrdb'] = go_term_xrdb

        if go_term['annotations']:
            if tags_dictionary and term_id in tags_dictionary:
                go_term['tags'] = tags_dictionary[term_id]['gs_tags']
            GO_terms.append(go_term)

    return GO_terms
