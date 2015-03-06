# -*- coding: utf-8 -*-
"""
    estimate.py

    :copyright: (c) 2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import ModelSQL, ModelView, fields
from trytond.pyson import Eval, Id, Bool
from decimal import Decimal
from trytond.pool import Pool

__all__ = ['Estimate']


class Estimate(ModelSQL, ModelView):
    "Estimate"

    __name__ = 'estimate.estimate'

    length = fields.Numeric(
        'Length', digits=(16, Eval('length_digits', 2)), required=True
    )
    length_uom = fields.Many2One(
        'product.uom', 'Length Uom',
        domain=[('category', '=', Id('product', 'uom_cat_length'))],
        states={
            'required': Bool(Eval('length')),
        }, depends=['length']
    )

    width = fields.Numeric(
        'Width', digits=(16, Eval('width_digits', 2)), required=True
    )

    width_uom = fields.Many2One(
        'product.uom', 'Width Uom',
        domain=[('category', '=', Id('product', 'uom_cat_length'))],
        states={
            'required': Bool(Eval('width')),
        },
        depends=['width']
    )

    distance = fields.Numeric("Distance ( In Miles)", required=True)

    number_of_steps = fields.Numeric(
        "Number Of Steps To The Deck", required=True
    )

    driving_time = fields.Function(
        fields.Numeric("Driving Time ( Hours)"), 'get_time'
    )
    deck_cleaning_time = fields.Function(
        fields.Numeric("Deck Cleaning Time (Hours)"), 'get_time'
    )
    step_cleaning_time = fields.Function(
         fields.Numeric("Step Cleaning Time ( Hours)"), 'get_time'
    )

    revenue = fields.Function(
        fields.Numeric("Revenue"), 'get_revenue'
    )

    @staticmethod
    def default_length_uom():
        UOM = Pool().get('product.uom')

        return UOM.search([('symbol', '=', 'in')], limit=1)[0].id

    @staticmethod
    def default_width_uom():
        UOM = Pool().get('product.uom')

        return UOM.search([('symbol', '=', 'in')], limit=1)[0].id

    def get_time(self, name):
        """
        Returns estimated hours for a job
        """
        if name == 'driving_time':
            return Decimal(self.distance) / 15

        if name == 'deck_cleaning_time':

            # TODO: Allow UOMs conversion
            return (self.length * 2) + (self.width * 3)

        if name == 'step_cleaning_time':
            return self.number_of_steps / 4

    def get_revenue(self, name):
        """
        Returns estimated revenue
        """
        return (self.driving_time / 4) + \
                (self.deck_cleaning_time + self.step_cleaning_time) * 70
