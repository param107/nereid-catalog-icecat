# -*- coding: utf-8 -*-
"""
    test_category

    Test tryton views and fields dependency.

    :copyright: (C) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import sys
import os
DIR = os.path.abspath(os.path.normpath(os.path.join(
    __file__, '..', '..', '..', '..', '..', 'trytond'
)))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))
import unittest

from lxml import objectify
from mock import Mock
import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT
from trytond.transaction import Transaction


class TestCategory(unittest.TestCase):
    '''
    Test product
    '''

    def setUp(self):
        """
        Set up data used in the tests.
        this method is called before each test function execution.
        """
        trytond.tests.test_tryton.install_module('nereid_catalog_icecat')

    def test0010categories(self):
        '''
        Test import with simple values
        '''
        Product = POOL.get('product.product')
        IRLang = POOL.get('ir.lang')
        TreeNode = POOL.get('product.tree_node')

        dir = os.path.dirname(__file__)
        objectified_xml = objectify.fromstring(
            open(os.path.join(dir, 'simple_product.xml')).read()
        )

        # get xml categories
        TreeNode._get_icecat_categorieslist_data = Mock(
            return_value=objectify.fromstring(
                open(os.path.join(dir, 'CategoriesList.xml')).read()
            ).xpath('//CategoriesList')[0]
        )

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            # set translatable languages
            de_de, = IRLang.search([('code', '=', 'de_DE')])
            de_de.translatable = True
            de_de.icecat_id = 2
            de_de.save()

            bg_bg, = IRLang.search([('code', '=', 'bg_BG')])
            bg_bg.translatable = True
            bg_bg.icecat_id = 20  # should not exist in test XML files
            bg_bg.save()

            cs_cz, = IRLang.search([('code', '=', 'cs_CZ')])
            cs_cz.translatable = True
            cs_cz.icecat_id = 3  # has empty string in XML
            cs_cz.save()

            # Import the product
            product = Product.create_from_icecat_data(objectified_xml)
            self.assertEqual(product.nodes[0].name, "monitors CRT")

            # Test if both translated values got saved
            with Transaction().set_context(language='de_DE'):
                product = Product(product.id)
                self.assertEqual(product.nodes[0].name, "monitoren CRT")

            with Transaction().set_context(language='bg_BG'):
                product = Product(product.id)
                self.assertEqual(product.nodes[0].name, "monitors CRT")

            with Transaction().set_context(language='cz_CZ'):
                product = Product(product.id)
                self.assertEqual(product.nodes[0].name, "monitors CRT")


def suite():
    """
    Define suite
    """
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestCategory)
    )
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
