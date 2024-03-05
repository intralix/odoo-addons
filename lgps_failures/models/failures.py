# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class Failures(models.Model):
    _inherit = 'repair.order'

    failures_categories_list_id = fields.Many2one(
        comodel_name="lgps.failures_categories_list",
        string=_("Failures Categories List"),
        ondelete="restrict",
        index=True,
    )

    failures_list_id = fields.Many2one(
        comodel_name="lgps.failures_list",
        string=_("Failures List"),
        ondelete="restrict",
        index=True,
    )

    failures_root_problem_list_id = fields.Many2one(
        comodel_name="lgps.failure_root_problem_list",
        string=_("Failures Root Problem List"),
        ondelete="restrict",
        index=True,
    )

    manipulation_detected = fields.Boolean(
        string=_("Detected Manipulation"),
        default=False
    )

    @api.onchange('product_id')
    def onchange_m2o(self):
        domain = {}
        if self.product_id:
            list_ids = []
            values = self.env['stock.production.lot'].search(
                [('product_id', '=', self.product_id.id)])

            for value in values:
                list_ids.append(value.id)

            domain = {
                'serial_number_id': [('id', 'in', list_ids)]
            }

        return {'domain': domain}

    @api.onchange('failures_categories_list_id')
    def _onchange_failures_categories_list_id(self):
        domain = {}
        if self.failures_categories_list_id:
            list_ids = []
            values = self.env['lgps.failures_list'].search([
                ('failures_categories_list_id', '=', self.failures_categories_list_id.id)
            ])

            for value in values:
                list_ids.append(value.id)

            self.product_id = []
            self.failures_list_id = []
            self.failures_root_problem_list_id = []

            domain = {
                'failures_list_id': [('id', 'in', list_ids)]
            }

        return {'domain': domain}

    @api.onchange('failures_list_id')
    def _onchange_failures_list_id(self):
        domain = {}
        if self.failures_list_id:
            list_ids = []
            values = self.env['lgps.failure_root_problem_list'].search([
                ('failures_list_ids', 'in', self.failures_list_id.id)
            ])

            for value in values:
                list_ids.append(value.id)

            self.failures_root_problem_list_id = []

            domain = {
                'failures_root_problem_list_id': [('id', 'in', list_ids)],
            }

        return {'domain': domain}
