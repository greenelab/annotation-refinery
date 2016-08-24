import unittest
from go import go
import download_files
import process_kegg
import process_go
import process_do
import loader

import logging


class DownloadTest(unittest.TestCase):
    """
    Tests for functions in download_files.py file
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testDownloadFilesNoSecretsLocation(self):
        """
        Test that the download_all_files() method raises SystemExit
        when asked to download files to process Disease Ontology but
        not passed a secrets_location.
        """
        with self.assertRaises(SystemExit) as se:
            download_files.download_all_files(
                'test_files/test_human.ini', 'test_files',
                secrets_location=None)

        self.assertEqual(se.exception.code, 1)


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
        kegg_info = process_kegg.get_kegg_info(
            'test_files/kegg_db_info')

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

        kegg_members_dict = process_kegg.get_kegg_sets_members(
            'test_files/KEGG/test_pathway.csv')

        desired_output = {
            'hsa00010': set(['10327', '124', '125', '126', '127', '128', '130',
                             '131', '130589', '160287']),
            'hsa00020': set(['1431', '1737', '1738', '1743', '2271', '3417',
                             '3418', '3419', '3420', '3421'])
        }

        self.assertEqual(kegg_members_dict, desired_output)

    def testGetKeggSetInfo(self):
        kegg_set_info = process_kegg.get_kegg_set_info(
            'test_files/KEGG/keggset_info_folder/hsa00010', 'homo-sapiens')

        desired_output = {
            'kegg_id': 'hsa00010',
            'title': 'KEGG-Pathway-hsa00010: Glycolysis / Gluconeogenesis'
                     ' - Homo sapiens (human)',
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
                'with minor variations of alternative paths [MD:M00003].',
            'slug': 'homo-sapiens-hsa00010'
        }

        self.assertEqual(kegg_set_info, desired_output)

    def testAddOrganismToSlug(self):
        kegg_set_info = process_kegg.get_kegg_set_info(
            'test_files/KEGG/keggset_info_folder/M00001', 'mus-musculus')

        desired_output = {
            'kegg_id': 'M00001',
            'title': 'KEGG-Module-M00001: Glycolysis '
                     '(Embden-Meyerhof pathway), glucose => pyruvate',
            'abstract': '',
            'slug': 'mus-musculus-m00001'
        }

        self.assertEqual(kegg_set_info, desired_output)

    def testBuildKeggSets(self):
        kegg_sets_members = process_kegg.get_kegg_sets_members(
            'test_files/KEGG/test_pathway.csv')
        test_keggsets = process_kegg.build_kegg_sets(
            kegg_sets_members, 'test_files/KEGG/keggset_info_folder',
            'Homo sapiens', 'Entrez')

        desired_keggsets = [
            {'kegg_id': 'hsa00010',
             'title': 'KEGG-Pathway-hsa00010: Glycolysis / Gluconeogenesis'
                      ' - Homo sapiens (human)',
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
             'annotations': {10327: [], 124: [], 125: [], 126: [],
                             127: [], 128: [], 130: [], 130589: [],
                             131: [], 160287: []},
             'slug': 'homo-sapiens-hsa00010',
             'xrdb': 'Entrez'},

            {'kegg_id': 'hsa00020',
             'title': 'KEGG-Pathway-hsa00020: Citrate cycle (TCA cycle)'
                      ' - Homo sapiens (human)',
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
             'annotations': {1431: [], 1737: [], 1738: [], 1743: [],
                             2271: [], 3417: [], 3418: [], 3419: [],
                             3420: [], 3421: []},
             'slug': 'homo-sapiens-hsa00020',
             'xrdb': 'Entrez'}
        ]

        self.assertEqual(test_keggsets, desired_keggsets)

    def testProcessKeggSets(self):
        all_kegg_sets = process_kegg.process_kegg_sets(
            'test_files/test_human.ini', 'test_files/')

        desired_keggsets = [
            {'kegg_id': 'hsa00010',
             'title': 'KEGG-Pathway-hsa00010: Glycolysis / Gluconeogenesis'
                      ' - Homo sapiens (human)',
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
             'annotations': {10327: [], 124: [], 125: [], 126: [],
                             127: [], 128: [], 130: [], 130589: [],
                             131: [], 160287: []},
             'slug': 'homo-sapiens-hsa00010',
             'xrdb': 'Entrez',
             # Tags added from test_KEGG_tags.txt mapping file
             'tags': ['alpha', 'beta', 'gamma', 'delta']},

            {'kegg_id': 'hsa00020',
             'title': 'KEGG-Pathway-hsa00020: Citrate cycle (TCA cycle)'
                      ' - Homo sapiens (human)',
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
             'annotations': {1431: [], 1737: [], 1738: [], 1743: [],
                             2271: [], 3417: [], 3418: [], 3419: [],
                             3420: [], 3421: []},
             'slug': 'homo-sapiens-hsa00020',
             'xrdb': 'Entrez',
             # Tags added from test_KEGG_tags.txt mapping file
             'tags': ['epsilon', 'zeta', 'eta', 'theta', 'iota']
             }
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
        assoc_file = 'test_files/GO/test_go_assoc_file.csv'
        evcodes = 'EXP, IDA, IPI, IMP, IGI, IEP'

        filtered_annotations = process_go.get_filtered_annotations(
            assoc_file, accepted_evcodes=evcodes)

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
            title = process_go.create_go_term_title(term)
            all_titles.add(title)

        desired_output = set([
            'GO-BP-0000005:premier league', 'GO-BP-0000003:eibar',
            'GO-BP-0000006:la liga', 'GO-BP-0000001:barcelona',
            'GO-BP-0000002:liverpool', 'GO-BP-0000007:european team'])

        self.assertEqual(all_titles, desired_output)

    def testCreateGOTermAbstractNoEvcodes(self):
        go_terms = self.gene_ontology.go_terms
        abstract = process_go.create_go_term_abstract(go_terms['GO:0000001'])
        desired_output = 'The distribution of mitochondria, including the ' + \
            'mitochondrial genome, into daughter cells after mitosis or ' + \
            'meiosis, mediated by interactions between mitochondria and ' + \
            'the cytoskeleton. Annotations are propagated through ' + \
            'transitive closure as recommended by the GO Consortium.'

        self.assertEqual(abstract, desired_output)

    def testCreateGOTermAbstractWithEvcodes(self):
        go_terms = self.gene_ontology.go_terms
        abstract = process_go.create_go_term_abstract(
            go_terms['GO:0000001'], ['IEP', 'IPI', 'IMP'])

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

        go_terms = process_go.process_go_terms(test_ini_file, 'test_files/')

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
             'annotations': {'A0A024QZP7': [], 'A0A024R216': [],
                             'A0A024R214': []},
             'xrdb': 'UniProtKB',
             'title': 'GO-BP-0000006:la liga',
             'slug': 'go0000006-homo-sapiens',
             'tags': ['xi', 'omicron', 'pi']},
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
             'annotations': {'A0A024R1V6': [], 'A0A024R214': [],
                             'A0A024QZP7': [], 'A0A024R216': []},
             'xrdb': 'UniProtKB',
             'title': 'GO-BP-0000007:european team',
             'slug': 'go0000007-homo-sapiens',
             'tags': ['rho', 'sigma']},
            {'abstract':
                "RZ - We're making this bogus term not OBSOLETE. Assists in "
                "the correct assembly of ribosomes or ribosomal subunits in "
                "vivo, but is not a component of the assembled ribosome when "
                "performing its normal biological function. Annotations are "
                "propagated through transitive closure as recommended by the "
                "GO Consortium. Only annotations with evidence coded as EXP, "
                "IDA, IPI, IMP, IGI or IEP are included.",
             'organism': 'Homo sapiens',
             'annotations': {'A0A024R214': []},
             'xrdb': 'UniProtKB',
             'title': 'GO-BP-0000005:premier league',
             'slug': 'go0000005-homo-sapiens',
             'tags': ['lambda', 'mu', 'nu']},
            {'abstract':
                'The maintenance of the structure and integrity of the '
                'mitochondrial genome; includes replication and segregation of'
                ' the mitochondrial chromosome. Annotations are propagated '
                'through transitive closure as recommended by the GO '
                'Consortium. Only annotations with evidence coded as EXP, '
                'IDA, IPI, IMP, IGI or IEP are included.',
             'organism': 'Homo sapiens',
             'annotations': {'A0A024R214': []},
             'xrdb': 'UniProtKB',
             'title': 'GO-BP-0000002:liverpool',
             'slug': 'go0000002-homo-sapiens',
             'tags': ['delta', 'epsilon', 'zeta']},
            {'abstract':
                'The production of new individuals that contain some portion '
                'of genetic material inherited from one or more parent '
                'organisms. Annotations are propagated through transitive '
                'closure as recommended by the GO Consortium. Only '
                'annotations with evidence coded as EXP, IDA, IPI, IMP, IGI '
                'or IEP are included.',
             'organism': 'Homo sapiens',
             'annotations': {'A0A024QZP7': [], 'A0A024R214': []},
             'xrdb': 'UniProtKB',
             'title': 'GO-BP-0000003:eibar',
             'slug': 'go0000003-homo-sapiens',
             'tags': ['eta', 'theta', 'iota']},
            {'abstract':
                'The distribution of mitochondria, including the '
                'mitochondrial genome, into daughter cells after mitosis or '
                'meiosis, mediated by interactions between mitochondria and '
                'the cytoskeleton. Annotations are propagated through '
                'transitive closure as recommended by the GO Consortium. Only'
                ' annotations with evidence coded as EXP, IDA, IPI, IMP, IGI '
                'or IEP are included.',
             'organism': 'Homo sapiens',
             'annotations': {'A0A024R216': []},
             'xrdb': 'UniProtKB',
             'title': 'GO-BP-0000001:barcelona',
             'slug': 'go0000001-homo-sapiens',
             'tags': ['alpha', 'beta', 'gamma']}
        ]

        self.assertEqual(go_terms, desired_output)

    def testHeadTermOBOFile(self):
        gene_ontology2 = go()
        loaded_obo_bool = gene_ontology2.load_obo(
                'test_files/test_go_obo_head_term.obo')
        self.assertEqual(loaded_obo_bool, True)
        self.assertEqual(gene_ontology2.heads, self.gene_ontology.heads)

    def testCorrectPublications(self):
        test_ini_file = 'test_files/test_zebrafish.ini'
        go_terms = process_go.process_go_terms(test_ini_file, 'test_files/')

        annotations = None
        for term in go_terms:
            if term['title'] == 'GO-BP-0009100:glycoprotein metabolic process':
                annotations = term['annotations']

        desired_annotations = {
            'ZDB-GENE-061110-16': [22522421, 22522421],
            'ZDB-GENE-040315-1': [19125692],
            'ZDB-GENE-030131-3222': [25609749],
            'ZDB-GENE-070412-4': [22522421],
            'ZDB-GENE-050213-1': [21294126],
            'ZDB-GENE-020419-3': [21294126, 22869369],
            'ZDB-GENE-030131-3127': [22869369],
            'ZDB-GENE-121129-1': [22869369],
            'ZDB-GENE-030131-9631': [16188232],
            'ZDB-GENE-010102-1': [19211552],
            'ZDB-GENE-060628-3': [16672343],
            'ZDB-GENE-030131-5186': [22869369],
            'ZDB-GENE-070112-1002': [20466645],
            'ZDB-GENE-011119-1': [21294126],
            'ZDB-GENE-040630-9': [16156897],
            'ZDB-GENE-040724-125': [21901110],
            'ZDB-GENE-030131-4714': [25505245],
            'ZDB-GENE-121001-5': [23359570],
            'ZDB-GENE-040801-234': [23768512],
            'ZDB-GENE-041124-3': [22869369, 15603738, 21294126],
            'ZDB-GENE-041124-2': [22869369, 15603738],
            'ZDB-GENE-050522-358': [23453667],
            'ZDB-GENE-111017-2': [21901110],
            'ZDB-GENE-030722-6': [22956764],
            'ZDB-GENE-020419-37': [20226781, 21294126,
                                   22869369, 20226781],
            'ZDB-GENE-070410-96': [22522421],
            'ZDB-GENE-060929-966': [20466645]}

        self.assertEqual(annotations, desired_annotations)

    def testPseudomonasSymbol(self):
        """
        Test to check that the output of Pseudomonas GO test files is what
        we expect, and that the 'xrdb' is 'Symbol', not 'PseudoCAP'.
        """
        test_ini_file = 'test_files/test_pseudomonas.ini'
        go_terms = process_go.process_go_terms(test_ini_file, 'test_files/')

        desired_go_term = None
        for term in go_terms:
            if term['title'] == 'GO-BP-0015838:amino-acid betaine transport':
                desired_go_term = term

        desired_go_term_info = {
            'title': 'GO-BP-0015838:amino-acid betaine transport',
            'abstract':
                'The directed movement of betaine, the N-trimethyl derivative '
                'of an amino acid, into, out of or within a cell, or between '
                'cells, by means of some agent such as a transporter or pore. '
                'Annotations are propagated through transitive closure as '
                'recommended by the GO Consortium. Only annotations with '
                'evidence coded as EXP, IDA, IPI, IMP, IGI or IEP '
                'are included.',
            'organism': 'Pseudomonas aeruginosa',
            'xrdb': 'Symbol',
            'slug': 'go0015838-pseudomonas-aeruginosa',
            'annotations': {'PA3236': [19919675], 'PA5388': [19919675]}
        }

        self.assertEqual(desired_go_term, desired_go_term_info)


class DO_Test(unittest.TestCase):
    """
    Test case for functions in process_do.py file
    """

    def setUp(self):
        """"""
        self.disease_ontology = go()
        self.loaded_obo_bool = self.disease_ontology.load_obo(
                'test_files/DO/test_do_obo_file.obo')

    def tearDown(self):
        """"""
        pass

    def testBuildOmimDict(self):
        do_obo_file = 'test_files/DO/test_do_obo_file.obo'

        doid_omim_dict = process_do.build_doid_omim_dict(do_obo_file)

        # Only one of the DO terms in the test DO OBO file has an
        # OMIM xref
        desired_output = {'DOID:9970': set(['601665'])}

        self.assertEqual(doid_omim_dict, desired_output)

    def testBuildMim2EntrezDict(self):
        mim2gene_file = 'test_files/DO/test_mim2gene.csv'

        mim2entrez_dict = process_do.build_mim2entrez_dict(mim2gene_file)

        desired_output = {'155541': '4160', '604630': '8431', '601487': '5468',
                          '605353': '51738', '176830': '5443',
                          '603128': '6492', '100640': '216', '616919': '22844',
                          '616923': '388591'}

        self.assertEqual(mim2entrez_dict, desired_output)

    def testBuildMimDiseasesDict(self):
        mim2gene_file = 'test_files/DO/test_mim2gene.csv'
        genemap_file = 'test_files/DO/test_genemap.csv'
        mim2entrez_dict = process_do.build_mim2entrez_dict(mim2gene_file)
        mim_diseases = process_do.build_mim_diseases_dict(genemap_file,
                                                          mim2entrez_dict)

        gene_tuples_dict = {}
        for mimid, mimdisease in mim_diseases.iteritems():
            gene_tuples_dict[mimid] = mimdisease.genetuples

        desired_gene_tuples = {
            '604367': [('5468', 'C')], '125853': [('5468', 'C')],
            '609734': [('5443', 'C')], '609338': [('5468', 'C')],
            '601665': [('8431', 'P'), ('5443', 'C'), ('51738', 'P'),
                       ('5468', 'C'), ('6492', 'C'), ('4160', 'C')]
        }

        phetypes_dict = {}
        for mimid, mimdisease in mim_diseases.iteritems():
            phetypes_dict[mimid] = mimdisease.phe_mm

        desired_phenotypes = {'604367': '(3)', '125853': '(3)',
                              '609734': '(3)', '609338': '(3)',
                              '601665': '(3)'}

        self.assertEqual(gene_tuples_dict, desired_gene_tuples)
        self.assertEqual(phetypes_dict, desired_phenotypes)

    def testAddDOTermAnnotations(self):
        do_obo_file = 'test_files/DO/test_do_obo_file.obo'
        doid_omim_dict = process_do.build_doid_omim_dict(do_obo_file)

        mim2gene_file = 'test_files/DO/test_mim2gene.csv'
        genemap_file = 'test_files/DO/test_genemap.csv'
        mim2entrez_dict = process_do.build_mim2entrez_dict(mim2gene_file)
        mim_diseases = process_do.build_mim_diseases_dict(genemap_file,
                                                          mim2entrez_dict)

        process_do.add_do_term_annotations(
            doid_omim_dict, self.disease_ontology, mim_diseases)

        # We know from testBuildOmimDict above that this is the only
        # one with OMIM xrefs
        doid = 'DOID:9970'
        do_term = self.disease_ontology.get_term(doid)

        annot_dict = {}

        for annotation in do_term.annotations:
            if annotation.gid not in annot_dict:
                annot_dict[annotation.gid] = []
            else:
                annot_dict[annotation.gid].append(annotation.ref)

        desired_annots = {4160: [], 8431: [], 51738: [], 5443: [],
                          5468: [], 6492: []}

        self.assertEqual(annot_dict, desired_annots)

    def testCreateDOTermTitle(self):
        title_set = set()

        for term_id, term in self.disease_ontology.go_terms.iteritems():
            term_title = process_do.create_do_term_title(term)
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
        do_obo_file = 'test_files/DO/test_do_obo_file.obo'
        doid_omim_dict = process_do.build_doid_omim_dict(do_obo_file)

        # We know from testBuildOmimDict above that this is the only
        # one with OMIM xrefs
        doid = 'DOID:9970'
        do_term = self.disease_ontology.get_term(doid)

        abstract = process_do.create_do_term_abstract(do_term, doid_omim_dict)
        desired_abstract = ' Annotations from child terms in the disease ' + \
            'ontology are propagated through transitive closure. ' + \
            'Annotations directly to this term are provided by the OMIM' + \
            ' disease ID 601665. Only annotations with confidence labeled' + \
            ' C or P by OMIM have been added.'
        self.assertEqual(abstract, desired_abstract)

    def testProcessDOTerms(self):
        test_ini_file = 'test_files/test_human.ini'

        do_terms = process_do.process_do_terms(test_ini_file)

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
             'annotations': {4160: [], 8431: [], 51738: [], 5443: [],
                             5468: [], 6492: []},
             'title': 'DO-374:nutrition disease',
             'slug': 'doid374-homo-sapiens',
             'tags': ['epsilon', 'zeta', 'eta', 'theta']},
            {'abstract':
                'A disease that involving errors in metabolic processes of '
                'building or degradation of molecules. Annotations from child'
                ' terms in the disease ontology are propagated through '
                'transitive closure. Only annotations with confidence labeled'
                ' C or P by OMIM have been added.',
             'xrdb': 'Entrez', 'organism': 'Homo sapiens',
             'annotations': {4160: [], 8431: [], 51738: [], 5443: [],
                             5468: [], 6492: []},
             'title': 'DO-0014667:disease of metabolism',
             'slug': 'doid0014667-homo-sapiens',
             'tags': ['alpha', 'beta', 'gamma', 'delta']},
            {'abstract': ' Annotations from child terms in the disease '
                'ontology are propagated through transitive closure. Only '
                'annotations with confidence labeled C or P by OMIM have been'
                ' added.',
             'xrdb': 'Entrez', 'organism': 'Homo sapiens',
             'annotations': {4160: [], 8431: [], 51738: [], 5443: [],
                             5468: [], 6492: []},
             'title': 'DO-654:overnutrition',
             'slug': 'doid654-homo-sapiens',
             'tags': ['nu', 'xi', 'omicron', 'omega']},
            {'abstract':
                'A disease is a disposition (i) to undergo pathological '
                'processes that (ii) exists in an organism because of one or'
                ' more disorders in that organism. Annotations from child '
                'terms in the disease ontology are propagated through '
                'transitive closure. Only annotations with confidence labeled'
                ' C or P by OMIM have been added.',
             'xrdb': 'Entrez', 'organism': 'Homo sapiens',
             'annotations': {4160: [], 8431: [], 51738: [], 5443: [],
                             5468: [], 6492: []},
             'title': 'DO-4:disease',
             'slug': 'doid4-homo-sapiens',
             'tags': ['iota', 'kappa', 'lambda', 'mu']},
            {'abstract': ' Annotations from child terms in the disease '
                'ontology are propagated through transitive closure. '
                'Annotations directly to this term are provided by the OMIM '
                'disease ID 601665. Only annotations with confidence labeled C'
                ' or P by OMIM have been added.',
             'xrdb': 'Entrez', 'organism': 'Homo sapiens',
             'annotations': {4160: [], 8431: [], 51738: [], 5443: [],
                             5468: [], 6492: []},
             'title': 'DO-9970:obesity',
             'slug': 'doid9970-homo-sapiens',
             'tags': ['upsilon', 'phi', 'chi', 'psi']},
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
             'annotations': {4160: [], 8431: [], 51738: [], 5443: [],
                             5468: [], 6492: []},
             'title': 'DO-0060158:acquired metabolic disease',
             'slug': 'doid0060158-homo-sapiens',
             'tags': ['pi', 'rho', 'sigma', 'tau']}
        ]

        self.assertEqual(do_terms, desired_output)


class LoaderTest(unittest.TestCase):
    """
    Test case for functions that load output from processed files into
    json and send them to Tribe
    """

    def setUp(self):
        """"""
        species_ini_file = 'test_files/test_human.ini'

        self.kegg_sets = process_kegg.process_kegg_sets(
            species_ini_file, 'test_files/')

        self.go_terms = process_go.process_go_terms(
            species_ini_file, 'test_files/')

        self.do_terms = process_do.process_do_terms(species_ini_file)

        self.main_config_file = 'test_files/test_main_config.ini'

    def tearDown(self):
        """"""
        pass

    def testLoadKEGGToTribe(self):
        geneset_response = loader.load_to_tribe(self.main_config_file,
                                                self.kegg_sets[0])

        self.assertEqual(
            geneset_response['title'], 'KEGG-Pathway-hsa00010: Glycolysis / '
                                       'Gluconeogenesis - Homo sapiens (human)')
        self.assertEqual(geneset_response['tip_item_count'], 10)

    def testLoadGOToTribe(self):
        geneset_response = loader.load_to_tribe(self.main_config_file,
                                                self.go_terms[0])

        self.assertEqual(geneset_response['title'],
                         'GO-BP-0000006:la liga')
        self.assertEqual(geneset_response['tip_item_count'], 3)

    def testLoadDOToTribe(self):
        geneset_response = loader.load_to_tribe(self.main_config_file,
                                                self.do_terms[0])

        self.assertEqual(geneset_response['title'], 'DO-374:nutrition disease')
        self.assertEqual(geneset_response['tip_item_count'], 6)

    """
    The next three tests check the creation of a new version of
    a geneset if the geneset already exists and the annotations have
    changed. For these tests, we will process the same geneset lists
    as the previous tests, but we will load the second geneset in each
    of those lists to Tribe.
    """
    def testCreateNewKEGGVersion(self):
        """
        Test adding one gene to an existing KEGG set
        """

        selected_kegg_term = self.kegg_sets[1]

        geneset_response = loader.load_to_tribe(self.main_config_file,
                                                selected_kegg_term,
                                                prefer_update=True)

        self.assertEqual(
            geneset_response['title'], 'KEGG-Pathway-hsa00020: Citrate cycle '
                                       '(TCA cycle) - Homo sapiens (human)')
        self.assertEqual(geneset_response['tip_item_count'], 10)

        # Adding random gene 5432
        selected_kegg_term['annotations'] = {
            1431: [], 1737: [], 1738: [], 1743: [], 2271: [], 3417: [],
            3418: [], 3419: [], 3420: [], 3421: [], 5432: []
        }

        version_response = loader.load_to_tribe(self.main_config_file,
                                                selected_kegg_term,
                                                prefer_update=True)

        self.assertEqual(len(version_response['annotations']), 11)

    def testCreateNewGOVersion(self):
        """
        Test removing one gene from an existing GO term
        """

        selected_go_term = self.go_terms[1]

        geneset_response = loader.load_to_tribe(
            self.main_config_file, selected_go_term, prefer_update=True)

        self.assertEqual(geneset_response['title'],
                         'GO-BP-0000007:european team')
        self.assertEqual(geneset_response['tip_item_count'], 4)

        # Remove gene 'A0A024R1V6'
        selected_go_term['annotations'] = {
            'A0A024R214': [], 'A0A024QZP7': [], 'A0A024R216': []}

        version_response = loader.load_to_tribe(
            self.main_config_file, selected_go_term, prefer_update=True)

        self.assertEqual(len(version_response['annotations']), 3)

    def testCreateNewDOVersion(self):
        """
        Test adding one term and removing one term from an existing DO term
        """

        selected_do_term = self.do_terms[1]

        geneset_response = loader.load_to_tribe(
            self.main_config_file, selected_do_term, prefer_update=True)

        self.assertEqual(geneset_response['title'],
                         'DO-0014667:disease of metabolism')
        self.assertEqual(geneset_response['tip_item_count'], 6)

        # Remove gene 5468, add random gene 4321
        selected_do_term['annotations'] = {
            4160: [], 8431: [], 51738: [], 5443: [], 6492: [], 4321: []}

        version_response = loader.load_to_tribe(
            self.main_config_file, selected_do_term, prefer_update=True)

        self.assertEqual(len(version_response['annotations']), 6)

    """
    The next test is similar to the three tests above, but it checks
    that if the geneset we want to create already exists and the
    annotations have not changed, we handle the situation appropriately.
    """

    def testCreatingAlreadyExistingGeneset(self):
        """
        Testing that if we try to create an already created geneset
        and annotations have not changed, fail gracefully.
        """

        selected_go_term = self.go_terms[2]

        geneset_response = loader.load_to_tribe(
            self.main_config_file, selected_go_term, prefer_update=True)

        self.assertEqual(geneset_response['title'],
                         'GO-BP-0000005:premier league')
        self.assertEqual(geneset_response['tip_item_count'], 1)

        # Do not change the annotations, just try to save to Tribe again
        response = loader.load_to_tribe(
            self.main_config_file, selected_go_term, prefer_update=True)

        self.assertEqual(response['status_code'], 409)
        self.assertEqual(
            response['content'], 'There is already a geneset with the slug '
            '"go0000005-homo-sapiens" and annotations {\'A0A024R214\': []} '
            'saved in Tribe. A new geneset has not been saved.')


if __name__ == '__main__':

    # Logging level can be input as an argument to logging.basicConfig()
    # function to get more logging output (e.g. level=logging.INFO)
    # The default level is logging.WARNING
    logging.basicConfig()

    unittest.main()
