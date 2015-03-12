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
        'Length', digits=(16, Eval('length_digits', 2))
    )
    length_uom = fields.Many2One(
        'product.uom', 'Length Uom',
        domain=[('category', '=', Id('product', 'uom_cat_length'))],
        states={
            'required': Bool(Eval('length')),
        }, depends=['length']
    )

    width = fields.Numeric(
        'Width', digits=(16, Eval('width_digits', 2))
    )

    width_uom = fields.Many2One(
        'product.uom', 'Width Uom',
        domain=[('category', '=', Id('product', 'uom_cat_length'))],
        states={
            'required': Bool(Eval('width')),
        },
        depends=['width']
    )

    distance = fields.Numeric("Distance ( In Miles)")

    number_of_steps = fields.Numeric(
        "Number Of Steps To The Deck")
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

class EstimateJobStart(ModelView):
	"Estimate Job Start"
	__name__ = 'estimate.estimate_job.start'

	estimate_Time_type = fields.Selection([
		('distance', Distance'),
		('area', 'Area'),
                ('steps', 'Number of steps')
        ], 'Estimate Time Type', required=True)

    length = fields.Numeric(
        'Length', digits=(16, Eval('length_digits', 2)),
	states={
		'invisible': Eval('estimate_time_type') != 'area',
		'required': Eval('estimate_time_type') == 'area',
  	 }, depends=['estimate_time_type)
    )
    length_uom = fields.Many2One(
        'product.uom', 'Length Uom',
        domain=[('category', '=', Id('product', 'uom_cat_length'))],
        states={
            'required': Bool(Eval('length')) & Eval('estimate_time_type') == 'area',
	    'invisible': ~(Bool(Eval('length')) & Eval('estimate_time_type') == 'area'),
        }, depends=['length', 'estimate_time_type']
    )

    width = fields.Numeric(
        'Width', digits=(16, 2),
            states={
                'invisible': Eval('estimate_time_type') != 'area',
                'required': Eval('estimate_time_type') == 'area',
         }, depends=['estimate_time_type) 
    )


    width_uom = fields.Many2One(
        'product.uom', 'Width Uom',
        domain=[('category', '=', Id('product', 'uom_cat_length'))],
        states={
            'required': Bool(Eval('length')) & Eval('estimate_time_type') == 'area',
            'invisible': ~(Bool(Eval('length')) & Eval('estimate_time_type') == 'area'),
        }, depends=['width', 'estimate_time_type']
    )

    distance = fields.Numeric("Distance ( In Miles)")
            states={
                'invisible': Eval('estimate_time_type') != 'distance',
                'required': Eval('estimate_time_type') == 'distance',
         }, depends=['estimate_time_type']
    )

    number_of_steps = fields.Numeric(
        "Number Of Steps To The Deck")
            states={
                'invisible': Eval('estimate_time_type') != 'steps',
                'required': Eval('estimate_time_type') == 'steps',
         }, depends=['estimate_time_type']
    )
	
class EstimateJob(Wizard):
	'Estimate Job'
	__name__ = 'estimate.estimate_job',
	start = StateView('estimate.estimate_job.start',
            'estimate.estimate_job_view_form', [
            Button('Cancel', 'end', 'tryton-cancel').
            Button('Estimate', 'estimate_', 'tryton-ok', default=True),
	    ])
	estimate_ = StateAction('estimate.act_estimate_form')

	def do_estimate(self, action):
	    Estimate = Pool.get('estimate.estimate')
               

