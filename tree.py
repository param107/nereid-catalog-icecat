# -*- coding: utf-8 -*-
'''

    nereid_catalog_icecat

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Ltd.
    :license: BSD, see LICENSE for more details

'''
import gzip
import os
from cStringIO import StringIO

from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from nereid.helpers import slugify
from trytond.config import CONFIG
import requests
from lxml import objectify

__all__ = ['Node']
__metaclass__ = PoolMeta


class Node:
    __name__ = "product.tree_node"

    icecat_id = fields.Integer('ICECAT Category ID')

    def _save_icecat_category_alternate_lang(self, data):
        """
        Save icecat categories in alternate languages

        :param data: lxml object for categorieslist
        """
        IrLang = Pool().get('ir.lang')

        languages = IrLang.search([
            ('translatable', '=', True),
            ('icecat_id', '!=', None),
        ])

        for language in languages:
            with Transaction().set_context(language=language.code):
                expression = 'Category[@ID="%d"]/Name[@langid="%d"]' % \
                             (self.icecat_id, language.icecat_id)
                try:
                    name, = data.xpath(expression)
                except ValueError:
                    continue
                name = name.get('Value')
                if not name:
                    # name is empty
                    continue
                self.write([self], {'name': name})

    @classmethod
    def _get_or_create_icecat_if_not_exists(cls, icecat_id):
        """
        Build TreeNode hierarchy for given category

        :param icecat_id: ICECAT category ID

        :returns: Node activerecord for icecat_id
        """
        data = cls._get_icecat_categorieslist_data()
        node = cls.search([('icecat_id', '=', icecat_id)])
        if node:
            # node already exists, simply return
            node, = node
        elif icecat_id == 1:
            # Create root node as it does not exist
            node, = cls.create([{
                'name': 'ICECAT Categories',  # since no name set in XML file
                'type_': 'catalog',
                'slug': slugify('ICECAT Categories'),
                'icecat_id': icecat_id
            }])
        else:
            category, = data.xpath(
                'Category[@ID="%d"]' % icecat_id
            )
            name, = category.xpath('Name[@langid="1"]')
            name = name.get('Value')
            node, = cls.create([{
                'name': name,
                'type_': 'catalog',
                'slug': slugify(name),
                'icecat_id': icecat_id
            }])
            node._save_icecat_category_alternate_lang(data)

            # get parent object and recursively create the tree
            parent, = category.xpath('ParentCategory')
            parent_node = cls._get_or_create_icecat_if_not_exists(
                int(parent.attrib.get('ID'))
            )
            cls.write([node], {'parent': parent_node})
        return node

    @staticmethod
    def _get_icecat_categorieslist_data():
        """
        Get CategoriesList.xml content from local if possible otherwise remote
        """
        directory = os.path.join(
            CONFIG['data_path'],
            Transaction().cursor.dbname,
            'nereid_catalog_icecat'
        )
        if not os.path.isdir(directory):
            os.makedirs(directory, 0660)

        filename = os.path.join(directory, "CategoriesList.xml")
        if not os.path.isfile(filename):
            categorieslist_url = "http://data.icecat.biz/export/freexml/refs/"\
                                 "CategoriesList.xml.gz"
            categorieslist = gzip.GzipFile(fileobj=StringIO(requests.get(
                categorieslist_url,
                auth=(CONFIG['icecat_username'], CONFIG['icecat_password'])
            ).content))

            categorieslist_content = categorieslist.read()
            with open(filename, 'w') as file_p:
                file_p.write(categorieslist_content)
            xml_content = categorieslist_content
        xml_content = open(filename).read()

        return objectify.fromstring(xml_content).xpath('//CategoriesList')[0]
