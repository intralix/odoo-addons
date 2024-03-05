# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class FailureOdt(models.Model):
    _inherit = 'project.task'

    repair_ids = fields.Many2one(
        comodel_name="repair.order",
        string=_("Failures"),
        index=True,
    )
