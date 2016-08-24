import sys
import json
import requests
from ConfigParser import SafeConfigParser

from utils import translate_gene_ids

# Import and set logger
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def load_to_tribe(main_config_file, geneset_info, prefer_update=False):
    """
    This function takes the passed geneset data (in the geneset_info
    dictionary) and attempts to create a new geneset or version
    of a geneset in Tribe using the helper functions in the tribe_client
    module. It reads the necessary username, password, tribe_id, and
    tribe_secret from the secrets file defined in the main_config_file
    and the Tribe location/url from this same main_config_file.

    *Note: This function depends on the tribe-client package, which must be
    installed in the same python environment as this function is run from.

    Arguments:
    main_config_file -- A string, location of the main INI configuration
    file. This file should include Tribe parameters and the location of
    the secrets file.

    geneset_info -- Dictionary containing the data for the geneset or
    version to be created. The geneset_info dictionary **must** contain
    a geneset 'title' and nonempty 'annotations' for a new geneset or
    geneset version to be created.
    This is an example of a geneset_info dictionary:

    geneset_info = {
        'title': 'DO-0014667:disease of metabolism',
        'abstract':
            'A disease that involving errors in metabolic processes of '
            'building or degradation of molecules. Annotations from child'
            ' terms in the disease ontology are propagated through '
            'transitive closure. Only annotations with confidence labeled'
            ' C or P by OMIM have been added.',
        'xrdb': 'Entrez',
        'organism': 'Homo sapiens',
        'annotations': {4160: [], 8431: [], 51738: [], 5443: [],
                        5468: [], 6492: []},

        'slug': 'doid0014667-homo-sapiens'
     }

    prefer_update -- Boolean keyword argument. If False, this function
    will not try to create new versions of already existing genesets - it will
    attempt to create a geneset in Tribe from the geneset_info and fail if
    the geneset (with the same title and creator username) already exists.
    If True, this function will check if a geneset with the same title
    and creator username exists. If no such geneset exists, it will create
    a new geneset, but if such geneset does exist, it will check if the
    annotations have changed. If the annotations have changed, it will
    create a new version of the geneset with the new annotations.
    If the annotations have not changed, no new geneset version will be saved.

    Returns:
    Either:
    a) response -- The response from Tribe, including a 'status_code' and
    'content'

    or b) False (and logs an error), if the geneset_info did not contain a
    title or annotations.

    """
    if 'title' not in geneset_info:
        logger.error('Data for geneset must contain a "title" key and value'
                     ' to be able to be saved to Tribe.')
        return False

    if 'annotations' not in geneset_info or geneset_info['annotations'] == []:
        logger.error('Data for geneset must contain a "annotations" key and '
                     'value to be able to be saved to Tribe. The value must '
                     'be a non-empty list of annotations.')
        return False

    try:
        from tribe_client.utils import obtain_token_using_credentials, \
            create_remote_geneset, create_remote_version
    except ImportError:
        logger.error('The package "tribe-client" has not been installed in '
                     'this Python environment. Please pip-install it to'
                     ' proceed.')
        sys.exit(1)

    mc_file = SafeConfigParser()
    mc_file.read(main_config_file)

    if not mc_file.has_section('Tribe parameters'):
        logger.error('Main INI config file has no "Tribe parameters" section, '
                     'which is needed to run the load_to_tribe function.')
        sys.exit(1)

    tribe_url = mc_file.get('Tribe parameters', 'TRIBE_URL')

    secrets_location = mc_file.get('main', 'SECRETS_FILE')
    secrets_file = SafeConfigParser()
    secrets_file.read(secrets_location)

    if not secrets_file.has_section('Tribe secrets'):
        logger.error('Secrets file has no "Tribe secrets" section, which is'
                     ' required to save the processed genesets to Tribe.')
        sys.exit(1)

    required_secrets = set(['tribe_id', 'tribe_secret', 'username',
                            'password'])
    secrets_set = set(secrets_file.options('Tribe secrets'))

    if not required_secrets.issubset(secrets_set):
        logger.error('Tribe secrets section must contain TRIBE_ID, '
                     'TRIBE_SECRET, USERNAME, and PASSWORD to be able to save'
                     ' processed genesets to Tribe.')
        sys.exit(1)

    tribe_id = secrets_file.get('Tribe secrets', 'TRIBE_ID')
    tribe_secret = secrets_file.get('Tribe secrets', 'TRIBE_SECRET')
    username = secrets_file.get('Tribe secrets', 'USERNAME')
    password = secrets_file.get('Tribe secrets', 'PASSWORD')

    access_token_url = tribe_url + '/oauth2/token/'
    access_token = obtain_token_using_credentials(
        username, password, tribe_id, tribe_secret, access_token_url)

    if prefer_update:

        gs_url = tribe_url + '/api/v1/geneset/' + username + '/' + \
            geneset_info['slug']

        parameters = {'oauth_consumer_key': access_token,
                      'full_annotations': 'true', 'show_tip': 'true',
                      'xrid': 'Entrez'}

        check_gs_request = requests.get(gs_url, params=parameters)

        if check_gs_request.status_code == 200:
            gs_response = check_gs_request.json()

            try:
                annotations = gs_response['tip']['annotations']
            except (KeyError, TypeError):
                # There was no 'tip' version for this geneset, create
                # first version.
                geneset_info['geneset'] = gs_response['resource_uri']
                geneset_info['description'] = 'Adding annotations.'
                response = create_remote_version(access_token, geneset_info,
                                                 tribe_url)
                return response

            old_annotations = {}
            for annotation in annotations:
                gene = annotation['gene']['entrezid']
                old_annotations[gene] = set()
                for pub in annotation['pubs']:
                    old_annotations[gene].add(pub['pmid'])

            gene_list = geneset_info['annotations'].keys()
            translate_response = translate_gene_ids(tribe_url, gene_list,
                                                    geneset_info['xrdb'],
                                                    'Entrez')
            if translate_response.status_code != 200:
                logger.error(('Tribe request to translate gene IDs with Tribe '
                              'url={0} gene_list={1} and from_id={2} failed.'
                              'Previous annotations could not be retrieved, '
                              'and new version of geneset with data {3} will '
                              'not be created.').format(tribe_url, gene_list,
                             geneset_info['xrdb'], geneset_info))
                return False

            gene_entrezids = translate_response.json()

            pub_set_annotations = {}
            for gene, publist in geneset_info['annotations'].iteritems():
                if gene in gene_entrezids:
                    if len(gene_entrezids[gene]) != 1:
                        logger.warning('There was more than one Entrez ID '
                                       'found for gene %s', gene)
                    gene = gene_entrezids[gene][0]
                    pub_set_annotations[gene] = set(publist)
                else:
                    logger.warning('No Entrez IDs were found for gene %s',
                                   gene)

            if pub_set_annotations != old_annotations:
                # Annotations have changed
                geneset_info['geneset'] = gs_response['resource_uri']
                geneset_info['parent'] = gs_response['tip']['resource_uri']
                geneset_info['description'] = 'Updating annotations.'

                response = create_remote_version(access_token, geneset_info,
                                                 tribe_url)
            else:
                # Do not create a new version or geneset
                logger.info('Geneset with title %s already exists with the '
                            'same annotations in Tribe. Not attempting to '
                            'save this geneset.', geneset_info['title'])
                response = {}
                response['content'] = (
                    'There is already a geneset with the slug "{0}" and '
                    'annotations {1} saved in Tribe. A new geneset has not '
                    'been saved.').format(geneset_info['slug'],
                                          geneset_info['annotations'])
                response['status_code'] = 409
        else:
            # No geneset with this geneset 'slug' and creator username exists
            # yet, so create it
            response = create_remote_geneset(access_token, geneset_info,
                                             tribe_url)

    else:
        response = create_remote_geneset(access_token, geneset_info,
                                         tribe_url)
    return response


def write_json_file(geneset_info, json_filename):
    with open(json_filename, "w") as outfile:
        json.dump(geneset_info, outfile, indent=2)
