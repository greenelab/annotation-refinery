import sys

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class idmap:
    key_val = None
    """
    Pass the filename of the key_value pair file.
    """
    def __init__(self, filename, list=None):
        self.key_val = {}
        idfile = list
        if filename is not None:
            idfile = open(filename)

        for line in idfile:
            toks = line.strip().upper().split('\t')
            if len(toks) < 2 or toks[0] == '':
                continue

            self.key_val[toks[0]] = tuple(toks[1:])

    def keys(self):
        if self.key_val is None:
            return {}
        else:
            return self.key_val.keys()

    def get(self, id=None):
        """
        Returns None if no file was loaded or if the key does not exist.
        """
        upper_id = None
        if id is not None:
            upper_id = id.upper()
        if self.key_val is None:
            logger.info('idmap::get called with no mapping file loaded')
            return None
        else:
            try:
                return self.key_val[upper_id]
            except KeyError:
                logger.warning('No match for %s', id)
                return None


if __name__ == '__main__':

    # Logging level can be input as an argument to logging.basicConfig()
    # function to get more logging output (e.g. level=logging.INFO)
    # The default level is logging.WARNING
    logging.basicConfig()

    from optparse import OptionParser
    usage = "usage: %prog [options]"
    parser = OptionParser(usage, version="%prog dev-unreleased")
    parser.add_option("-i", "--input-file", dest="input",
                      help="input file", metavar="FILE")
    parser.add_option("-m", "--mappings-file", dest="mapping",
                      help="mappings file", metavar="FILE")
    parser.add_option("-c", "--col", dest="col", help="column to remap")
    parser.add_option("-s", "--skip", dest="skip",
                      help="lines to skip (i.e. just print the first S lines)",
                      default=0)
    (options, args) = parser.parse_args()

    if options.input is None:
        sys.stderr.write("--input-file is required.\n")
        sys.exit()
    if options.mapping is None:
        sys.stderr.write("--mappings-file is required.\n")
        sys.exit()
    col = None
    if options.col:
        col = int(options.col)

    id_name = idmap(options.mapping)

    for (i, line) in enumerate(open(options.input)):
        if (i < int(options.skip)):
            print(line.rstrip('\n'))
            continue
        if col is not None:
            toks = line.rstrip('\n').split('\t')
            matches = id_name.get(toks[col])
            if matches is None:
                continue
            for match in matches:
                toks[col] = match
                print('\t'.join(toks))
        else:
            vals = id_name.get(line.strip())
            if vals is None:
                continue
            for val in vals:
                print(val)
