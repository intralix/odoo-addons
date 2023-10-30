# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class FailureOdt(models.Model):
    _inherit = 'project.task'

    failures_ids = fields.One2many(
        comodel_name="lgps.failures",
        inverse_name="repairs_id",
        string=_("Failures"),
        index=True,
    )

    repairs_count = fields.Integer(
        string=_("ODTs"),
        compute='_compute_repairs_count',
    )

    def _compute_repairs_count(self):
        for rec in self:
            rec.repairs_count = self.env['project.task'].search_count(
                [('failures_id', '=', rec.id)])
