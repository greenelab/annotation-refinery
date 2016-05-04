import sys
import gzip
from ConfigParser import SafeConfigParser

from go import go

# Import and set logger
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


GO_NAMESPACE_MAP = {
    'biological_process': 'BP',
    'molecular_function': 'MF',
    'cellular_component': 'CC',
}


def get_filtered_annotations(assoc_file, accepted_evcodes=None,
                             leading_gene_id=None):
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

    leading_gene_id -- True or False value. For some organisms, such as Mouse,
    there is a leading tag on the gene IDs column in the gene association file.
    This tag is just a duplicate of the type of gene identifier (already
    present in the identifier type (xrdb) column) and should be removed to get
    the pure gene ID (e.g. to get "99668" as opposed to "MGI:99668").

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
        (xrdb, xrid, details, goid, refstring, ev_code, date) = (
            toks[0], toks[1], toks[3], toks[4], toks[5], toks[6], toks[13])

        if leading_gene_id:
            xrid = xrid.split(':')[1]

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

    obo_url = species_file.get('GO', 'GO_OBO_URL')
    assoc_file_url = species_file.get('GO', 'ASSOC_FILE_URL')

    obo_filename = obo_url.split('/')[-1]
    assoc_filename = assoc_file_url.split('/')[-1]
    obo_file = base_download_folder + obo_filename
    assoc_file = sd_folder + 'GO/' + assoc_filename

    evcodes = species_file.get('GO', 'EVIDENCE_CODES')
    evcodes = evcodes.replace(' ', '').split(',')

    leading_gene_id = False
    if species_file.has_option('GO', 'LEADING_GENE_ID'):
        leading_gene_id = species_file.getboolean('GO', 'LEADING_GENE_ID')

    annotations = get_filtered_annotations(assoc_file, evcodes,
                                           leading_gene_id=leading_gene_id)

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

    for (term_id, term) in gene_ontology.go_terms.iteritems():

        if not term.annotations:
            continue

        go_term = {}
        go_term['title'] = create_go_term_title(term)
        go_term['abstract'] = create_go_term_abstract(term, evcodes)
        go_term['organism'] = organism

        go_term['annotations'] = {}
        go_term_xrdb = None

        for annotation in term.annotations:
            if annotation.gid not in go_term['annotations']:
                go_term['annotations'][annotation.gid] = []
            else:
                go_term['annotations'][annotation.gid].append(annotation.ref)

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
            GO_terms.append(go_term)

    return GO_terms
