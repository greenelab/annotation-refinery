import unittest
from process_kegg import *
from process_go import *
from process_do import *
from go import go


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
        kegg_set_info = get_kegg_set_info('test_files/sample_set_info.csv')

        desired_output = {
            'title': 'Glycolysis / Gluconeogenesis - Homo sapiens (human)',
            'abstract':
                'Glycolysis is the process of converting glucose into pyruvate'
                ' and generating small amounts of ATP (energy) and NADH '
                '(reducing power). It is a central pathway that produces '
                'important precursor metabolites: six-carbon compounds of '
                'glucose-6P and fructose-6P and three-carbon compounds of '
                'glycerone-P, glyceraldehyde-3P, glycerate-3P, '
                'phosphoenolpyruvate, and pyruvate [MD:M00001]. Acetyl-CoA,'
                ' another important precursor metabolite, is produced by '
                'oxidative decarboxylation of pyruvate [MD:M00307]. '
                'When the enzyme genes of this pathway are examined in '
                'completely sequenced genomes, the reaction steps of '
                'three-carbon compounds from glycerone-P to pyruvate form'
                ' a conserved core module [MD:M00002], which is found in '
                'almost all organisms and which sometimes contains operon'
                ' structures in bacterial genomes. Gluconeogenesis is a '
                'synthesis pathway of glucose from noncarbohydrate '
                'precursors. It is essentially a reversal of glycolysis '
                'with minor variations of alternative paths [MD:M00003].'
        }

        self.assertEqual(kegg_set_info, desired_output)

    def testProcessKeggSets(self):
        pass


class GO_Test(unittest.TestCase):
    """
    Test case for functions in process_go.py file
    """

    def setUp(self):
        """"""
        self.gene_ontology = go()
        self.loaded_obo_bool = self.gene_ontology.load_obo(
                'test_files/test_go_obo_file.csv')

    def tearDown(self):
        """"""
        pass

    def testGetFilteredAnnotations(self):
        assoc_file = 'test_files/test_go_assoc_file.csv'
        evcodes = 'EXP, IDA, IPI, IMP, IGI, IEP'
        filtered_annotations = get_filtered_annotations(assoc_file, evcodes)
        desired_output = [
            ('UniProtKB', 'A0A024QZP7', 'GO:0000004', 'GO_REF:0000052', '20101115'),
            ('UniProtKB', 'A0A024QZP7', 'GO:0000003', 'GO_REF:0000052', '20101115'),
            ('UniProtKB', 'A0A024R1V6', 'GO:0000007', 'GO_REF:0000052', '20141106'),
            ('UniProtKB', 'A0A024R214', 'GO:0000003', 'GO_REF:0000052', '20141106'),
            ('UniProtKB', 'A0A024R214', 'GO:0000002', 'GO_REF:0000052', '20141106'),
            ('UniProtKB', 'A0A024R216', 'GO:0000001', 'GO_REF:0000052', '20110516')]

        self.assertEqual(filtered_annotations, desired_output)

    def testCreateGOTermTitle(self):
        all_titles = set()

        for (term_id, term) in self.gene_ontology.go_terms.iteritems():
            title = create_go_term_title(term)
            all_titles.add(title)

        desired_output = set([
            'GO-MF-0000005:Premier League', 'GO-BP-0000003:Eibar',
            'GO-MF-0000006:La Liga', 'GO-BP-0000001:Barcelona',
            'GO-BP-0000002:Liverpool', 'GO-MF-0000007:European team'])

        self.assertEqual(all_titles, desired_output)

    def testCreateGOTermAbstractNoEvcodes(self):
        go_terms = self.gene_ontology.go_terms
        abstract = create_go_term_abstract(go_terms['GO:0000001'])
        desired_output = 'The distribution of mitochondria, including the ' + \
            'mitochondrial genome, into daughter cells after mitosis or ' + \
            'meiosis, mediated by interactions between mitochondria and ' + \
            'the cytoskeleton. Annotations are propagated through ' + \
            'transitive closure as recommended by the GO Consortium.'

        self.assertEqual(abstract, desired_output)

    def testCreateGOTermAbstractWithEvcodes(self):
        go_terms = self.gene_ontology.go_terms
        abstract = create_go_term_abstract(go_terms['GO:0000001'],
                                           ['IEP', 'IPI', 'IMP'])
        desired_output = 'The distribution of mitochondria, including the ' + \
            'mitochondrial genome, into daughter cells after mitosis or ' + \
            'meiosis, mediated by interactions between mitochondria and ' + \
            'the cytoskeleton. Annotations are propagated through ' + \
            'transitive closure as recommended by the GO Consortium.' + \
            ' Only annotations with evidence coded as IEP, IPI or IMP' + \
            ' are included.'

        self.assertEqual(abstract, desired_output)

    def testProcessGOTerms(self):
        pass


class DO_Test(unittest.TestCase):
    """
    Test case for functions in process_do.py file
    """

    def setUp(self):
        """"""

    def tearDown(self):
        """"""
        pass

    def testCreateDOTermTitle(self):
        pass

    def testCreateDOAbstractTitle(self):
        pass

    def testBuildOmimDict(self):
        do_obo_file = 'test_files/test_do_obo_file.csv'

        omim_dict = build_doid_omim_dict(do_obo_file)

        # Only one of the DO terms in the test DO OBO file has an
        # OMIM xref
        desired_output = {'DOID:9970': set(['601665'])}

        self.assertEqual(omim_dict, desired_output)

    def testBuildMim2GeneDict(self):
        mim2gene_file = 'test_files/test_mim2gene.csv'

        mim2gene_dict = build_mim2gene_dict(mim2gene_file)

        desired_output = {'100725': '1145', '100730': '1146', '100720': '1144',
                          '100740': '43', '616876': '', '616877': '',
                          '100880': '48', '616872': '56889', '100650': '217',
                          '100790': '429', '100850': '50', '100660': '218',
                          '100670': '219', '100710': '1140', '100690': '1134',
                          '616874': '51643', '100678': '39', '100640': '216'}

        self.assertEqual(mim2gene_dict, desired_output)

    def testBuildGenemapDict(self):
        genemap_file = ''

        genemap_dict = build_genemap_dict(mim2gene_file)

    def testProcessDOTerms(self):
        pass


if __name__ == '__main__':
    unittest.main()
