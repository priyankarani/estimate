# -*- coding: utf-8 -*-
"""
    estimate.py

    :copyright: (c) 2015 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import ModelSQL, ModelView, fields
from trytond.wizard import Wizard, StateView, StateTransition, Button
from trytond.pyson import Eval, Id, Bool
from decimal import Decimal
from trytond.pool import Pool
from trytond.transaction import Transaction

__all__ = ['Estimate', 'EstimateJobResult', 'EstimateJobStart', 'EstimateJob']


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


class EstimateJobStart(ModelView):
    "Estimate Job Start"
    __name__ = 'estimate.estimate_job.start'

    estimate_time_type = fields.Selection([
        ('distance', 'Distance'),
        ('area', 'Area'),
        ('steps', 'Number of steps')
    ], 'Estimate Time Type', required=True)

    estimated_result = fields.Numeric("Esimated Result")


class EstimateJobResult(ModelView):
    'Estimate Job'
    __name__ = 'estimate.estimate_job.result'

    message = fields.Text("Message", readonly=True)


class EstimateJob(Wizard):
    'Estimate Job'
    __name__ = 'estimate.estimate_job'

    start = StateView(
        'estimate.estimate_job.start',
        'estimate.estimate_job_view_form_start', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('OK', 'estimate_', 'tryton-ok', default=True),
        ]
    )
    estimate_ = StateTransition()
    result = StateView(
        'estimate.estimate_job.result',
        'estimate.estimate_job_view_form_result', [
            Button('Ok', 'end', 'tryton-ok', default=True),
        ]
    )

    def transition_estimate_(self):
        """
        Estimate result and proceed to next state
        """
        return 'result'

    def _calculate_hours(self):
        Estimate = Pool().get('estimate.estimate')

        estimate = Estimate(Transaction().context.get('active_id'))

        type = self.start.estimate_time_type
        if type == 'area':
            return Decimal(
                (estimate.length * 2) + (estimate.width * 3)
            )

        elif type == 'driving_time':
            return Decimal(estimate.distance / 15)

        elif type == 'steps':
            return Decimal(estimate.number_of_steps / 4)

    def default_result(self, data):
        message = "Estimated %s is %d" % (
            self.start.estimate_time_type, self._calculate_hours()
        )

        return {
            'message': message
        }
