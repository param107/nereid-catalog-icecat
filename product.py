# -*- coding: utf-8 -*-
'''

    nereid_catalog_icecat

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Ltd.
    :license: BSD, see LICENSE for more details

'''
from trytond.pool import Pool, PoolMeta

__all__ = ['Product']
__metaclass__ = PoolMeta


class Product:
    __name__ = 'product.product'

    def _add_icecat_categories(self, data):
        """
        Add icecat categories to current product

        :param data: lxml objectified record of the product
        """
        TreeNode = Pool().get('product.tree_node')

        new_node = TreeNode._get_or_create_icecat_if_not_exists(
            int(data.Product.Category.get('ID'))
        )

        # add category to product
        self.write([self], {
            'nodes': [('add', [new_node])]
        })

    @classmethod
    def create_from_icecat_data(cls, data):
        """
        Create the product using super but also add nodes

        :param data: lxml objectified record of the product
        """
        product = super(Product, cls).create_from_icecat_data(data)
        product._add_icecat_categories(data)
        return product
