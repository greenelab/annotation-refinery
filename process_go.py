from go import go
from ConfigParser import SafeConfigParser

# Import and set logger
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


GO_NAMESPACE_MAP = {
        'biological_process': 'BP',
        'molecular_function': 'MF',
        'cellular_component': 'CC',
}


def get_filtered_annotations(assoc_file, accepted_evcodes):
    """
    This function reads in the association file and returns a list of
    only the annotations that have evidence codes in 'accepted_evcodes'
    """

    annotations = []
    assoc_fh = open(assoc_file, 'r')

    for line in assoc_fh:
        if line.startswith('!'):
            continue

        toks = line.strip().split('\t')
        (xrdb, xrid, details, goid, ref, ev_code, date) = (
            toks[0], toks[1], toks[3], toks[4], toks[5], toks[6], toks[13])

        if details == 'NOT':
            continue

        if accepted_evcodes is not None and (ev_code not in accepted_evcodes):
            continue

        annotation = (xrdb, xrid, goid, ref, date)

        annotations.append(annotation)

    return annotations


def create_go_term_title(go_term):
    """
    """
    go_id = go_term.go_id.split(':')[1]

    namespace = GO_NAMESPACE_MAP[go_term.get_namespace()]

    title = 'GO' + '-' + namespace + '-' + go_id + ':' + go_term.full_name

    return title


def create_go_term_abstract(go_term, evlist=None):
    """
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
        return description
    else:
        logger.info("No description on term %s", go_term)
        return None


def process_go_terms(species_ini_file):
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

    evcodes = species_file.get('GO', 'EVIDENCE_CODES')
    assoc_file = species_file.get('GO', 'ASSOCIATION_FILE')
    obo_location = species_file.get('GO', 'GO_OBO_FILE')
    organism = species_file.get('species_info', 'SCIENTIFIC_NAME')

    annotations = get_filtered_annotations(assoc_file, evcodes)

    gene_ontology = go()
    loaded_obo_bool = gene_ontology.load_obo(obo_location)

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
                                     date=date, direct=True)

    gene_ontology.populated = True
    gene_ontology.propagate()

    GO_terms = []

    for (term_id, term) in gene_ontology.go_terms.iteritems():

        if not term.annotations:
            continue

        go_term = {}
        go_term['annotations'] = term.annotations
        go_term['title'] = create_go_term_title(term)
        go_term['abstract'] = create_go_term_abstract(term, evcodes)
        go_term['organism'] = organism

        GO_terms.append(go_term)

    return GO_terms
