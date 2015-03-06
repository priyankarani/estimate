# -*- coding: utf-8 -*-
"""
    __init__.py

    :copyright: (c) 2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool

from estimate import Estimate


def register():
    Pool.register(
        Estimate,
        module='estimate', type_='model'
    )
