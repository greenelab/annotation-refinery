import sys
import json
from ConfigParser import SafeConfigParser

# Import and set logger
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def load_to_tribe(species_ini_file, geneset_info):
    try:
        from tribe_client.utils import obtain_token_using_credentials, \
            create_remote_geneset
    except ImportError:
        logger.error('The package "tribe-client" has not been installed in '
                     'this Python environment. Please pip-install it to'
                     ' proceed.')
        sys.exit(1)

    species_file = SafeConfigParser()
    species_file.read(species_ini_file)

    if not species_file.has_section('Tribe parameters'):
        logger.error('Species INI file has no "Tribe parameters" section, '
                     'which is needed to run the load_to_Tribe function.')
        sys.exit(1)

    tribe_url = species_file.get('Tribe parameters', 'TRIBE_URL')

    secrets_location = species_file.get('Tribe parameters', 'SECRETS_FILE')
    secrets_file = SafeConfigParser()
    secrets_file.read(secrets_location)

    if not secrets_file.has_section('Tribe secrets'):
        logger.error('Secrets file has no "Tribe secrets" section, which is'
                     'required to save the processed genesets to Tribe.')
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

    geneset_response = create_remote_geneset(access_token, geneset_info,
                                             tribe_url)

    return geneset_response


def return_as_json(geneset_info):
    geneset_json = json.dumps(geneset_info)
    return geneset_json
