import sys
import requests
from ConfigParser import SafeConfigParser

from utils import translate_gene_ids

# Import and set logger
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# All of these functions depend on the tribe-client package, which must be
# installed in the same python environment where the functions are run from.
try:
    from tribe_client.utils import obtain_token_using_credentials, \
            create_remote_geneset, create_remote_version, \
            download_organism_public_genesets
except ImportError:
    logger.error('The package "tribe-client" has not been installed in '
                 'this Python environment. Please pip-install it to'
                 ' proceed.')
    sys.exit(1)


def get_oauth_token(tribe_url, secrets_location):
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
    return access_token


def load_to_tribe(main_config_file, geneset_info, access_token,
                  prefer_update=False):
    """
    This function takes the passed geneset data (in the geneset_info
    dictionary) and attempts to create a new geneset or version
    of a geneset in Tribe using the helper functions in the tribe_client
    module. It reads the necessary username, password, tribe_id, and
    tribe_secret from the secrets file defined in the main_config_file
    and the Tribe location/url from this same main_config_file.

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

    access token -- A string. Tribe OAuth2 token returned by the
    get_oauth_token() function above. This is required to create gene sets in
    the desired Tribe instance.

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

    username = secrets_file.get('Tribe secrets', 'USERNAME')

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

                logger.info('Creating new version for geneset %s',
                            geneset_info['title'])
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
                # Tribe gene translator returns all search keys as strings
                gene = str(gene)
                if gene in gene_entrezids:
                    if len(gene_entrezids[gene]) != 1:
                        logger.warning('There was more than one Entrez ID '
                                       'found for gene %s', gene)
                    gene = gene_entrezids[gene][0]
                    pub_set_annotations[gene] = set(publist)
                else:
                    logger.warning('No Entrez IDs were found for gene %s '
                                   'and cross-reference DB %s.',
                                   gene, geneset_info['xrdb'])

            if pub_set_annotations != old_annotations:
                # Annotations have changed
                geneset_info['geneset'] = gs_response['resource_uri']
                geneset_info['parent'] = gs_response['tip']['resource_uri']
                geneset_info['description'] = 'Updating annotations.'

                logger.info('Creating new version for geneset %s',
                            geneset_info['title'])
                response = create_remote_version(access_token, geneset_info,
                                                 tribe_url)
            else:
                # Do not create a new version or geneset
                logger.info('Geneset with title %s already exists with the '
                            'same annotations in Tribe. Not attempting to '
                            'save a new geneset nor geneset version.',
                            geneset_info['title'])
                response = {}
                response['content'] = (
                    'There is already a geneset with the slug "{0}" and '
                    'annotations {1} saved in Tribe. Neither a geneset nor '
                    'a geneset version have been created.').format(
                        geneset_info['slug'], geneset_info['annotations'])
                response['status_code'] = 409
        else:
            # No geneset with this geneset 'slug' and creator username exists
            # yet, so create it
            logger.info('Creating geneset %s', geneset_info['title'])
            response = create_remote_geneset(access_token, geneset_info,
                                             tribe_url)

    else:
        logger.info('Creating geneset %s', geneset_info['title'])
        response = create_remote_geneset(access_token, geneset_info,
                                         tribe_url)
    return response


def compare_genesets(tribe_genesets, processed_genesets):
    tribe_geneset_dict = {}
    proc_geneset_dict = {}

    changed_genesets = []

    # We will use the gene set 'slugs' as the identifiers for each gene set
    for gs in tribe_genesets:
        tribe_geneset_dict[gs['slug']] = gs

    for gs in processed_genesets:
        proc_geneset_dict[gs['slug']] = gs

    changed_ctr = 0
    unchanged_ctr = 0
    for k, v in proc_geneset_dict.iteritems():
        # Try to get the corresponding tribe gene set (if it exists) using
        # the slug, which is the key in this proc_geneset_dict. Otherwise,
        # add to changed_genesets.
        try:
            corr_tribe_gs = tribe_geneset_dict[k]
        except KeyError:
            logger.info('New gene set with slug %s is being added.',
                        v['slug'])
            changed_genesets.append(v)
            changed_ctr += 1
            continue

        # Publications must be converted to a set instead of a list, because
        # the ones in the retrieved gene sets may be the same as the ones in
        # the processed gene sets, but just in a different order.
        processed_annotations = {}
        for gid, pub_list in v['annotations'].iteritems():
            processed_annotations[gid] = set(pub_list)

        retrieved_annotations = {}
        if corr_tribe_gs['tip'] is None:
            logger.info('Gene set with slug %s had no "tip" version. '
                        'Adding to list of gene set versions to be created.',
                        v['slug'])
            changed_genesets.append(v)
            changed_ctr += 1
            continue

        for annotation in corr_tribe_gs['tip']['annotations']:
            gene = annotation['gene']
            xrdb = v['xrdb']

            # Get desired gene identifier
            if xrdb == 'Entrez':
                gene = gene['entrezid']
            elif xrdb == 'Symbol':
                gene = gene['systematic_name']
            else:
                gene = gene['xrid']

            pubs = set()

            for pub in annotation['pubs']:
                pubs.add(pub['pmid'])

            retrieved_annotations[gene] = pubs

        if processed_annotations != retrieved_annotations:
            logger.debug('Annotations for gene set with slug %s have changed -'
                         ' Adding to list of gene set versions to be created.',
                         corr_tribe_gs['slug'])
            changed_genesets.append(v)
            changed_ctr += 1

        else:
            unchanged_ctr += 1
    logger.info('%s gene sets have changed, saving them to Tribe', changed_ctr)
    logger.info('%s gene sets were unchanged', unchanged_ctr)
    return changed_genesets


def get_changed_genesets(species_file, secrets_file, processed_genesets,
                         access_token):
    species_fh = SafeConfigParser()
    species_fh.read(species_file)
    species_name = species_fh.get('species_info', 'SCIENTIFIC_NAME')

    secrets_fh = SafeConfigParser()
    secrets_fh.read(secrets_file)
    creator_username = secrets_fh.get('Tribe secrets', 'USERNAME')

    all_changed_genesets = []

    # Put all gene sets that have annotations in a common xrid inside
    # a list in the genesets_by_xrid dictionary.
    genesets_by_xrid = {}
    for geneset in processed_genesets:
        key = geneset['xrdb']
        if key in genesets_by_xrid:
            genesets_by_xrid[key].append(geneset)
        else:
            genesets_by_xrid[key] = []

    logger.info('The processed gene sets contain the following '
                'cross-reference gene identifiers: %s',
                genesets_by_xrid.keys())

    for xrid, proc_geneset_list in genesets_by_xrid.iteritems():
        tribe_geneset_dict = download_organism_public_genesets(
            species_name, creator_username=creator_username,
            request_params={'xrid': xrid, 'full_annotations': 'true',
                            'oauth_consumer_key': access_token}
        )
        tribe_geneset_list = []
        for k, v in tribe_geneset_dict.iteritems():
            tribe_geneset_list.extend(v)

        logger.info('%s existing gene sets were retrieved from Tribe',
                    len(tribe_geneset_list))

        changed_genesets = compare_genesets(tribe_geneset_list,
                                            proc_geneset_list)
        all_changed_genesets.extend(changed_genesets)

    return all_changed_genesets
