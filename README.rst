===================
Annotation Refinery
===================

The Annotation Refinery python package consists of functions that process
publicly available annotated sets of genes, such as Gene Ontology and Disease
Ontology terms.


Configuration files
-------------------

The Annotation Refinery requires at least two ``.ini`` configuration files in
the main directory to run:

1. A ``main_config.ini`` file with the main configuration settings, and

2. At least one ``<species>.ini`` file, which will contain the locations of
   the desired annotation files for that species, amon other things. Users can
   add configuration files in the main directory for as many species as
   they want the refinery to process.


Optionally, there can also be a ``secrets.ini`` file, which stores values like
usernames and passwords for access to restricted URLs.


The Main Configuration File
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The main configuration file includes settings like the location(s) of the
species file(s), where the output of the refinery (the processed genesets)
should be loaded to, where annotation files should be downloaded to, 
and optionally, the location of the secrets file.

.. code-block::

    [main]
    SECRETS_FILE: secrets.ini
    PROCESS_TO: Tribe


    # All other download folders in this files should be folders within
    # this root folder
    [download_folder]
    BASE_DOWNLOAD_FOLDER: download_files


    [Tribe parameters]
    TRIBE_URL: https://tribe.greenelab.com


    [species files]
    SPECIES_FILES: human.ini


The Species File(s)
~~~~~~~~~~~~~~~~~~~

Each species file should contain the URLs of the desired annotation files to be
downloaded.

.. code-block::

    # File for human settings

    [species_info]
    SCIENTIFIC_NAME: Homo sapiens
    TAXONOMY_ID: 9606


    # ***********************************************
    # Below, add as sections the types of annotations
    # that should be downloaded and processed
    # ***********************************************

    [GO]
    DOWNLOAD: TRUE
    GO_OBO_URL: ftp://ftp.geneontology.org/go/ontology/obo_format_1_2/gene_ontology.1_2.obo
    ASSOC_FILE_URL: ftp://ftp.geneontology.org/go/gene-associations/gene_association.goa_human.gz
    DOWNLOAD_FOLDER: download_files/GO

    OBO_FILE: download_files/GO/gene_ontology.1_2.obo
    ASSOC_FILE: download_files/GO/gene_association.goa_human.gz

    # We want to filter GO terms so that we only process the ones with the
    # following evidence codes:
    EVIDENCE_CODES: EXP, IDA, IPI, IMP, IGI, IEP


    [DO]
    DOWNLOAD: TRUE
    DO_OBO_URL: http://sourceforge.net/p/diseaseontology/code/HEAD/tree/trunk/HumanDO.obo?format=raw
    MIM2GENE_URL: http://omim.org/static/omim/data/mim2gene.txt
    GENEMAP_URL: http://data.omim.org/downloads/<SecretKey>/genemap.txt
    DOWNLOAD_FOLDER: download_files/DO

    DO_OBO_FILE: download_files/DO/HumanDO.obo?format=raw
    MIM2GENE_FILE: download_files/DO/mim2gene.txt
    GENEMAP_FILE: download_files/DO/genemap.txt


The Secrets File
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The secrets file contains things like usernames and passwords for databases,
secret keys for APIs where annotation files will be downloaded from, etc.

.. code-block::

    [OMIM API secrets]
    SECRET_KEY: ExampleSecretKey

    [Tribe secrets]
    TRIBE_ID: asdf1234
    TRIBE_SECRET: qwerty1234

    USERNAME: example_username
    PASSWORD: password


Instructions for getting an OMIM API secret key can be found here:
http://omim.org/downloads

Instructions for getting the Tribe secrets can be found here:
http://tribe-greenelab.readthedocs.io/en/latest/api.html#creating-new-resources-through-tribe-s-api
