===================
Annotation Refinery
===================

The Annotation Refinery python package consists of functions that process
publicly available annotated sets of genes, such as Gene Ontology terms.


Configuration files
-------------------

This refinery requires at least two ``.ini`` configuration files in the main
directory to run:

1. A ``main_config.ini`` file with the main configuration settings, and

2. At least one ``<species>.ini`` file, which will contain the locations of
   the desired annotation files for that species, amon other things. Users can
   add configuration files in the main directory for as many species as
   they want the refinery to process.


Optionally, there can also be a ``secrets.ini`` file, which stores values like
usernames and passwords for access to restricted URLs.

Examples of these files are in the main repository.


Secrets file
______________

Instructions for getting the Tribe secrets can be found here:
http://tribe-greenelab.readthedocs.io/en/latest/api.html#creating-new-resources-through-tribe-s-api

Instructions for getting an OMIM API secret key can be found here:
http://omim.org/downloads
