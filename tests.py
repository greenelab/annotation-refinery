import unittest
from go import go
from process_kegg import *
from process_go import *
from process_do import *

# Import and set logger
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


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
        kegg_info = get_kegg_info('test_files/test_keggdb_info.csv')

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
        kegg_set_info = get_kegg_set_info(
            'test_files/test_keggset_info_folder/hsa00010')

        desired_output = {
            'kegg_id': 'hsa00010',
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

    def testBuildKeggSets(self):
        kegg_sets_members = get_kegg_sets_members(
            'test_files/test_kegg_members.csv')
        test_keggsets = build_kegg_sets(kegg_sets_members,
                                        'test_files/test_keggset_info_folder',
                                        'Homo sapiens')

        desired_keggsets = [
            {'kegg_id': 'hsa00010',
             'title': 'Glycolysis / Gluconeogenesis - Homo sapiens (human)',
             'organism': 'Homo sapiens',
             'abstract':
                 'Glycolysis is the process of converting glucose into '
                 'pyruvate and generating small amounts of ATP (energy) and '
                 'NADH (reducing power). It is a central pathway that produces'
                 ' important precursor metabolites: six-carbon compounds of '
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
                 'with minor variations of alternative paths [MD:M00003].',

             # These are the only genes in our test_kegg_members.csv file
             # for this KEGG set
             'annotations': set([('10327', None), ('124', None), ('125', None),
                                 ('126', None), ('127', None), ('128', None),
                                 ('130', None), ('130589', None),
                                 ('131', None), ('160287', None)])},

            {'kegg_id': 'hsa00020',
             'title': 'Citrate cycle (TCA cycle) - Homo sapiens (human)',
             'organism': 'Homo sapiens',
             'abstract':
                'The citrate cycle (TCA cycle, Krebs cycle) is an important '
                'aerobic pathway for the final steps of the oxidation of '
                'carbohydrates and fatty acids. The cycle starts with '
                'acetyl-CoA, the activated form of acetate, derived from '
                'glycolysis and pyruvate oxidation for carbohydrates and from '
                'beta oxidation of fatty acids. The two-carbon acetyl group in'
                ' acetyl-CoA is transferred to the four-carbon compound of '
                'oxaloacetate to form the six-carbon compound of citrate. In a'
                ' series of reactions two carbons in citrate are oxidized to '
                'CO2 and the reaction pathway supplies NADH for use in the '
                'oxidative phosphorylation and other metabolic processes. The '
                'pathway also supplies important precursor metabolites '
                'including 2-oxoglutarate. At the end of the cycle the '
                'remaining four-carbon part is transformed back to '
                'oxaloacetate. According to the genome sequence data, many '
                'organisms seem to lack genes for the full cycle [MD:M00009], '
                'but contain genes for specific segments [MD:M00010 M00011].',

             # These are the only genes in our test_kegg_members.csv file
             # for this KEGG set
             'annotations': set([('1431', None), ('1737', None),
                                 ('1738', None), ('1743', None),
                                 ('2271', None), ('3417', None),
                                 ('3418', None), ('3419', None),
                                 ('3420', None), ('3421', None)])}
        ]

        self.assertEqual(test_keggsets, desired_keggsets)

    def testProcessKeggSets(self):
        all_kegg_sets = process_kegg_sets('test_files/test_human.ini')

        desired_keggsets = [
            {'kegg_id': 'hsa00010',
             'title': 'Glycolysis / Gluconeogenesis - Homo sapiens (human)',
             'organism': 'Homo sapiens',
             'abstract':
                 'Glycolysis is the process of converting glucose into '
                 'pyruvate and generating small amounts of ATP (energy) and '
                 'NADH (reducing power). It is a central pathway that produces'
                 ' important precursor metabolites: six-carbon compounds of '
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
                 'with minor variations of alternative paths [MD:M00003].',

             # These are the only genes in our test_kegg_members.csv file
             # for this KEGG set
             'annotations': set([('10327', None), ('124', None), ('125', None),
                                 ('126', None), ('127', None), ('128', None),
                                 ('130', None), ('130589', None),
                                 ('131', None), ('160287', None)])},

            {'kegg_id': 'hsa00020',
             'title': 'Citrate cycle (TCA cycle) - Homo sapiens (human)',
             'organism': 'Homo sapiens',
             'abstract':
                'The citrate cycle (TCA cycle, Krebs cycle) is an important '
                'aerobic pathway for the final steps of the oxidation of '
                'carbohydrates and fatty acids. The cycle starts with '
                'acetyl-CoA, the activated form of acetate, derived from '
                'glycolysis and pyruvate oxidation for carbohydrates and from '
                'beta oxidation of fatty acids. The two-carbon acetyl group in'
                ' acetyl-CoA is transferred to the four-carbon compound of '
                'oxaloacetate to form the six-carbon compound of citrate. In a'
                ' series of reactions two carbons in citrate are oxidized to '
                'CO2 and the reaction pathway supplies NADH for use in the '
                'oxidative phosphorylation and other metabolic processes. The '
                'pathway also supplies important precursor metabolites '
                'including 2-oxoglutarate. At the end of the cycle the '
                'remaining four-carbon part is transformed back to '
                'oxaloacetate. According to the genome sequence data, many '
                'organisms seem to lack genes for the full cycle [MD:M00009], '
                'but contain genes for specific segments [MD:M00010 M00011].',

             # These are the only genes in our test_kegg_members.csv file
             # for this KEGG set
             'annotations': set([('1431', None), ('1737', None),
                                 ('1738', None), ('1743', None),
                                 ('2271', None), ('3417', None),
                                 ('3418', None), ('3419', None),
                                 ('3420', None), ('3421', None)])}
        ]
        self.assertEqual(all_kegg_sets, desired_keggsets)


class GO_Test(unittest.TestCase):
    """
    Test case for functions in process_go.py file
    """

    def setUp(self):
        """"""
        self.gene_ontology = go()
        self.loaded_obo_bool = self.gene_ontology.load_obo(
                'test_files/test_go_obo_file.obo')

    def tearDown(self):
        """"""
        pass

    def testGetFilteredAnnotations(self):
        assoc_file = 'test_files/test_go_assoc_file.csv'
        evcodes = 'EXP, IDA, IPI, IMP, IGI, IEP'
        filtered_annotations = get_filtered_annotations(assoc_file,
                                                        accepted_evcodes=evcodes)
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
            'GO-BP-0000005:premier league', 'GO-BP-0000003:eibar',
            'GO-BP-0000006:la liga', 'GO-BP-0000001:barcelona',
            'GO-BP-0000002:liverpool', 'GO-BP-0000007:european team'])

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
        test_ini_file = 'test_files/test_human.ini'

        go_terms = process_go_terms(test_ini_file)

        desired_output = [
            {'abstract':
                'Enables the transfer of a solute or solutes from one side of '
                'a membrane to the other according to the reaction: Zn2+(out) '
                '= Zn2+(in), probably powered by proton motive force. In '
                'high-affinity transport the transporter is able to bind the '
                'solute even if it is only present at very low concentrations.'
                ' Annotations are propagated through transitive closure as '
                'recommended by the GO Consortium. Only annotations with '
                'evidence coded as EXP, IDA, IPI, IMP, IGI or IEP are '
                'included.',
             'organism': 'Homo sapiens',
             'annotations': set([('A0A024QZP7', None), ('A0A024R216', None),
                                 ('A0A024R214', None)]),
             'xrdb': 'UniProtKB',
             'title': 'GO-BP-0000006:la liga'},
            {'abstract':
                'Catalysis of the transfer of a solute or solutes '
                'from one side of a membrane to the other according to the '
                'reaction: Zn2+ = Zn2+, probably powered by proton motive '
                'force. In low-affinity transport the transporter is able to '
                'bind the solute only if it is present at very high '
                'concentrations. Annotations are propagated through transitive'
                ' closure as recommended by the GO Consortium. Only '
                'annotations with evidence coded as EXP, IDA, IPI, IMP, IGI or'
                ' IEP are included.',
             'organism': 'Homo sapiens',
             'annotations': set([('A0A024R1V6', None), ('A0A024R214', None),
                                 ('A0A024QZP7', None), ('A0A024R216', None)]),
             'xrdb': 'UniProtKB',
             'title': 'GO-BP-0000007:european team'},
            {'abstract':
                "RZ - We're making this bogus term not OBSOLETE. Assists in "
                "the correct assembly of ribosomes or ribosomal subunits in "
                "vivo, but is not a component of the assembled ribosome when "
                "performing its normal biological function. Annotations are "
                "propagated through transitive closure as recommended by the "
                "GO Consortium. Only annotations with evidence coded as EXP, "
                "IDA, IPI, IMP, IGI or IEP are included.",
             'organism': 'Homo sapiens',
             'annotations': set([('A0A024R214', None)]),
             'xrdb': 'UniProtKB',
             'title': 'GO-BP-0000005:premier league'},
            {'abstract':
                'The maintenance of the structure and integrity of the '
                'mitochondrial genome; includes replication and segregation of'
                ' the mitochondrial chromosome. Annotations are propagated '
                'through transitive closure as recommended by the GO '
                'Consortium. Only annotations with evidence coded as EXP, '
                'IDA, IPI, IMP, IGI or IEP are included.',
             'organism': 'Homo sapiens',
             'annotations': set([('A0A024R214', None)]),
             'xrdb': 'UniProtKB',
             'title': 'GO-BP-0000002:liverpool'},
            {'abstract':
                'The production of new individuals that contain some portion '
                'of genetic material inherited from one or more parent '
                'organisms. Annotations are propagated through transitive '
                'closure as recommended by the GO Consortium. Only '
                'annotations with evidence coded as EXP, IDA, IPI, IMP, IGI '
                'or IEP are included.',
             'organism': 'Homo sapiens',
             'annotations': set([('A0A024QZP7', None), ('A0A024R214', None)]),
             'xrdb': 'UniProtKB',
             'title': 'GO-BP-0000003:eibar'},
            {'abstract':
                'The distribution of mitochondria, including the '
                'mitochondrial genome, into daughter cells after mitosis or '
                'meiosis, mediated by interactions between mitochondria and '
                'the cytoskeleton. Annotations are propagated through '
                'transitive closure as recommended by the GO Consortium. Only'
                ' annotations with evidence coded as EXP, IDA, IPI, IMP, IGI '
                'or IEP are included.',
             'organism': 'Homo sapiens',
             'annotations': set([('A0A024R216', None)]),
             'xrdb': 'UniProtKB',
             'title': 'GO-BP-0000001:barcelona'}]
        self.assertEqual(go_terms, desired_output)

    def testHeadTermOBOFile(self):
        gene_ontology2 = go()
        loaded_obo_bool = gene_ontology2.load_obo(
                'test_files/test_go_obo_head_term.obo')
        self.assertEqual(loaded_obo_bool, True)
        self.assertEqual(gene_ontology2.heads, self.gene_ontology.heads)


class DO_Test(unittest.TestCase):
    """
    Test case for functions in process_do.py file
    """

    def setUp(self):
        """"""
        self.disease_ontology = go()
        self.loaded_obo_bool = self.disease_ontology.load_obo(
                'test_files/test_do_obo_file.obo')

    def tearDown(self):
        """"""
        pass

    def testBuildOmimDict(self):
        do_obo_file = 'test_files/test_do_obo_file.obo'

        doid_omim_dict = build_doid_omim_dict(do_obo_file)

        # Only one of the DO terms in the test DO OBO file has an
        # OMIM xref
        desired_output = {'DOID:9970': set(['601665'])}

        self.assertEqual(doid_omim_dict, desired_output)

    def testBuildMim2EntrezDict(self):
        mim2gene_file = 'test_files/test_mim2gene.csv'

        mim2entrez_dict = build_mim2entrez_dict(mim2gene_file)

        desired_output = {'100725': '1145', '100730': '1146', '100720': '1144',
                          '100740': '43', '616876': '', '616877': '',
                          '100880': '48', '616872': '56889', '100650': '217',
                          '100790': '429', '100850': '50', '100660': '218',
                          '100670': '219', '100710': '1140', '100690': '1134',
                          '616874': '51643', '100678': '39', '100640': '216'}

        self.assertEqual(mim2entrez_dict, desired_output)

    def testBuildMimDiseasesDict(self):
        mim2gene_file = 'test_files/test_mim2gene.csv'
        genemap_file = 'test_files/test_genemap.csv'
        mim2entrez_dict = build_mim2entrez_dict(mim2gene_file)
        mim_diseases = build_mim_diseases_dict(genemap_file, mim2entrez_dict)

        gene_tuples_dict = {}
        for mimid, mimdisease in mim_diseases.iteritems():
            gene_tuples_dict[mimid] = mimdisease.genetuples

        desired_gene_tuples = {
            '265000': [('1146', 'C')], '605809': [('1145', 'C')],
            '608930': [('1134', 'C')], '608931': [('1145', 'C')],
            '616324': [('1145', 'C')], '601462': [('1134', 'C')],
            '616322': [('1144', 'C')], '209880': [('429', 'C')],
            '253290': [('1144', 'C'), ('1134', 'C'), ('1146', 'C')],
            '616313': [('1140', 'C')], '614559': [('50', 'C')],
            '610251': [('217', 'C')]}

        phetypes_dict = {}
        for mimid, mimdisease in mim_diseases.iteritems():
            phetypes_dict[mimid] = mimdisease.phe_mm

        desired_phenotypes = {
            '265000': '(3)', '605809': '(3)', '608930': '(3)', '608931': '(3)',
            '616324': '(3)', '601462': '(3)', '616322': '(3)', '209880': '(3)',
            '253290': '(3)', '616313': '(3)', '614559': '(3)', '610251': '(3)'}

        self.assertEqual(gene_tuples_dict, desired_gene_tuples)
        self.assertEqual(phetypes_dict, desired_phenotypes)

    def testAddDOTermAnnotations(self):
        do_obo_file = 'test_files/test_do_obo_file.obo'
        doid_omim_dict = build_doid_omim_dict(do_obo_file)

        # *NOTE: Here we will use an actual downloaded mim2gene.txt file
        # (instead of a test one), so that it gets all the Entrez IDs we need.
        mim2gene_file = 'download_files/DO/mim2gene.txt'
        genemap_file = 'test_files/test_genemap.csv'
        mim2entrez_dict = build_mim2entrez_dict(mim2gene_file)
        mim_diseases = build_mim_diseases_dict(genemap_file, mim2entrez_dict)

        add_do_term_annotations(doid_omim_dict, self.disease_ontology,
                                mim_diseases)

        # We know from testBuildOmimDict above that this is the only
        # one with OMIM xrefs
        doid = 'DOID:9970'
        do_term = self.disease_ontology.get_term(doid)

        annotation_set = set()

        for annotation in do_term.annotations:
            annotation_set.add((annotation.gid, annotation.ref))

        desired_annots = set([(4160, None), (8431, None), (51738, None),
                              (5443, None), (5468, None), (6492, None)])

        self.assertEqual(annotation_set, desired_annots)

    def testCreateDOTermTitle(self):
        title_set = set()

        for term_id, term in self.disease_ontology.go_terms.iteritems():
            term_title = create_do_term_title(term)
            title_set.add(term_title)

        desired_output = set([
            'DO-9970:obesity', 'DO-9972:hypervitaminosis A',
            'DO-0001816:angiosarcoma', 'DO-4:disease', 'DO-1115:sarcoma',
            'DO-0014667:disease of metabolism', 'DO-374:nutrition disease',
            'DO-0050687:cell type cancer',
            'DO-0060158:acquired metabolic disease',
            'DO-14566:disease of cellular proliferation',
            'DO-9971:hypervitaminosis D',
            'DO-654:overnutrition', 'DO-162:cancer'])

        self.assertEqual(title_set, desired_output)

    def testCreateDOAbstractTitle(self):
        do_obo_file = 'test_files/test_do_obo_file.obo'
        doid_omim_dict = build_doid_omim_dict(do_obo_file)

        # We know from testBuildOmimDict above that this is the only
        # one with OMIM xrefs
        doid = 'DOID:9970'
        do_term = self.disease_ontology.get_term(doid)

        abstract = create_do_term_abstract(do_term, doid_omim_dict)
        desired_abstract = ' Annotations from child terms in the disease ' + \
            'ontology are propagated through transitive closure. ' + \
            'Annotations directly to this term are provided by the OMIM' + \
            ' disease ID 601665. Only annotations with confidence labeled' + \
            ' C or P by OMIM have been added.'
        self.assertEqual(abstract, desired_abstract)

    def testProcessDOTerms(self):
        test_ini_file = 'test_files/test_human.ini'

        do_terms = process_do_terms(test_ini_file)

        desired_output = [
            {'abstract':
                'An acquired metabolic disease that is characterized by an '
                'insufficient intake of food or of certain nutrients, by an '
                'inability of the body to absorb and use nutrients, or by '
                'overconsumption of certain foods. Annotations from child '
                'terms in the disease ontology are propagated through '
                'transitive closure. Only annotations with confidence '
                'labeled C or P by OMIM have been added.',
             'xrdb': 'Entrez', 'organism': 'Homo sapiens',
             'annotations': set([(4160, None), (8431, None), (51738, None),
                                 (5443, None), (5468, None), (6492, None)]),
             'title': 'DO-374:nutrition disease'},
            {'abstract':
                'A disease that involving errors in metabolic processes of '
                'building or degradation of molecules. Annotations from child'
                ' terms in the disease ontology are propagated through '
                'transitive closure. Only annotations with confidence labeled'
                ' C or P by OMIM have been added.',
             'xrdb': 'Entrez', 'organism': 'Homo sapiens',
             'annotations': set([(4160, None), (8431, None), (51738, None),
                                 (5443, None), (5468, None), (6492, None)]),
             'title': 'DO-0014667:disease of metabolism'},
            {'abstract': ' Annotations from child terms in the disease '
                'ontology are propagated through transitive closure. Only '
                'annotations with confidence labeled C or P by OMIM have been'
                ' added.',
             'xrdb': 'Entrez', 'organism': 'Homo sapiens',
             'annotations': set([(4160, None), (8431, None), (51738, None),
                                (5443, None), (6492, None), (5468, None)]),
             'title': 'DO-654:overnutrition'},
            {'abstract':
                'A disease is a disposition (i) to undergo pathological '
                'processes that (ii) exists in an organism because of one or'
                ' more disorders in that organism. Annotations from child '
                'terms in the disease ontology are propagated through '
                'transitive closure. Only annotations with confidence labeled'
                ' C or P by OMIM have been added.',
             'xrdb': 'Entrez', 'organism': 'Homo sapiens',
             'annotations': set([(4160, None), (8431, None), (51738, None),
                                 (5443, None), (5468, None), (6492, None)]),
             'title': 'DO-4:disease'},
            {'abstract': ' Annotations from child terms in the disease '
                'ontology are propagated through transitive closure. '
                'Annotations directly to this term are provided by the OMIM '
                'disease ID 601665. Only annotations with confidence labeled C'
                ' or P by OMIM have been added.',
             'xrdb': 'Entrez', 'organism': 'Homo sapiens',
             'annotations': set([(4160, None), (8431, None), (51738, None),
                                 (5443, None), (5468, None), (6492, None)]),
             'title': 'DO-9970:obesity'},
            {'abstract':
                'A disease of metabolism that has _material_basis_in enzyme'
                ' deficiency or accumulation of enzymes or toxins which '
                'interfere with normal function due to an endocrine organ '
                'disease, organ malfunction, inadequate intake, dietary '
                'deficiency, or malabsorption. Annotations from child terms '
                'in the disease ontology are propagated through transitive '
                'closure. Only annotations with confidence labeled C or P by'
                ' OMIM have been added.',
             'xrdb': 'Entrez', 'organism': 'Homo sapiens',
             'annotations': set([(4160, None), (8431, None), (51738, None),
                                 (5443, None), (6492, None), (5468, None)]),
             'title': 'DO-0060158:acquired metabolic disease'}
        ]

        self.assertEqual(do_terms, desired_output)


if __name__ == '__main__':

    # Logging level can be input as an argument to logging.basicConfig()
    # function to get more logging output (e.g. level=logging.INFO)
    # The default level is logging.WARNING
    logging.basicConfig(level=logging.INFO)

    unittest.main()
