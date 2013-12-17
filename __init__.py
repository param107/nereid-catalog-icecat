# -*- coding: utf-8 -*-
'''

    nereid_catalog_icecat

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Ltd.
    :license: BSD, see LICENSE for more details

'''

from trytond.pool import Pool
from product import Product
from tree import Node


def register():
    """
    Register classes
    """
    Pool.register(
        Product,
        Node,
        module='nereid_catalog_icecat', type_='model'
    )
