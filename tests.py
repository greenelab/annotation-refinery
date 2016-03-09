import unittest
import os

from process_kegg import *


class KeggTest(unittest.TestCase):
    """
    Test case for functions in process_kegg.py file
    """

    def setUp(self):
        """"""
        pass

    def tearDown(self):
        """"""
        pass

    def testGetKeggInfo(self):
        """"""
        kegg_info = get_kegg_info('test_files/sample_kegg_info.csv')

        desired_output = {
            'brite': '148,770 entries',
            'enzyme': '6,666 entries',
            'lab_info': 'Kanehisa Laboratories',
            'title': 'Kyoto Encyclopedia of Genes and Genomes',
            'orthology': '19,301 entries',
            'genes': '18,661,136 entries',
            'disease': '1,477 entries',
            'module': '347,124 entries', 'glycan': '10,989 entries',
            'reaction': '10,045 entries', 'environ': '850 entries',
            'drug': '10,333 entries', 'compound': '17,578 entries',
            'release': 'Release 77.0+/03-07, Mar 16',
            'rclass': '3,014 entries', 'dgenes': '602,101 entries',
            'pathway': '427,122 entries', 'rpair': '15,278 entries',
            'genome': '4,165 entries'}

        self.assertEqual(kegg_info, desired_output)

    def testGetMembersInKeggSets(self):
        """"""

        kegg_members_dict = get_kegg_sets_members(
                'test_files/test_kegg_members.csv')

        desired_output = {
            'hsa00010': set(['10327', '124', '125', '126', '127', '128', '130',
                             '131', '130589', '160287']),
            'hsa00020': set(['1431', '1737', '1738', '1743', '2271', '3417',
                             '3418', '3419', '3420', '3421'])
            }

        self.assertEqual(kegg_members_dict, desired_output)

    def testGetKeggSetInfo(self):
        sample_set_info_filename = 'test_files/sample_set_info.csv'

    def testAssembleKeggSets(self):
        pass


if __name__ == '__main__':
    unittest.main()
