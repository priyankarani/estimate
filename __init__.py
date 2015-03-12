# -*- coding: utf-8 -*-
"""
    __init__.py

    :copyright: (c) 2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool

from estimate import Estimate, EstimateJobResult, EstimateJobStart, EstimateJob


def register():
    Pool.register(
        Estimate,
        EstimateJobResult,
        EstimateJobStart,
        module='estimate', type_='model'
    )
    Pool.register(
        EstimateJob,
        module='estimate', type_='wizard'
    )
