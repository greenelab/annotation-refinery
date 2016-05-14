import sys
import json
import requests
from ConfigParser import SafeConfigParser

from utils import translate_gene_ids

# Import and set logger
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def load_to_tribe(main_config_file, geneset_info, create_new_versions=False):
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

    if create_new_versions:

        gs_url = tribe_url + '/api/v1/geneset/' + username + '/' + \
            geneset_info['slug']

        parameters = {'oauth_consumer_key': access_token,
                      'full_annotations': 'true', 'show_tip': 'true',
                      'xrid': 'Entrez'}

        check_gs_request = requests.get(gs_url, params=parameters)

        if check_gs_request.status_code == 200:
            gs_response = check_gs_request.json()
            annotations = gs_response['tip']['annotations']

            old_annotations = {}
            for annotation in annotations:
                gene = annotation['gene']['entrezid']
                old_annotations[gene] = set(annotation['pubs'])

            gene_list = geneset_info['annotations'].keys()
            gene_entrezids = translate_gene_ids(tribe_url, gene_list,
                                                geneset_info['xrdb'], 'Entrez')

            pub_set_annotations = {}
            for gene, publist in geneset_info['annotations'].iteritems():
                if gene in gene_entrezids:
                    if len(gene_entrezids[gene]) != 1:
                        logger.warning('There was more than one Entrez ID '
                                       'found for gene %s', gene)
                    gene = gene_entrezids[gene][0]
                else:
                    logger.warning('No Entrez IDs were found for gene %s',
                                   gene)

                pub_set_annotations[gene] = set(publist)

            if pub_set_annotations != old_annotations:
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
                response['status_code'] = 400
        else:
            # No geneset with this geneset 'slug' and creator username exists
            # yet, so create it
            response = create_remote_geneset(access_token, geneset_info,
                                             tribe_url)

    else:
        response = create_remote_geneset(access_token, geneset_info,
                                         tribe_url)

    return response


def return_as_json(geneset_info):
    geneset_json = json.dumps(geneset_info)
    return geneset_json
