# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class RmaGpsDevice(models.Model):
    _inherit = 'lgps.device'

    rma_ids = fields.One2many(
        comodel_name="lgps.rma_process",
        inverse_name="device_id",
        string=_("RMAs"),
    )

    rma_count = fields.Integer(
        string=_('RMA Count'),
        compute='_compute_rma_count',
    )

    def _compute_rma_count(self):
        for rec in self:
            rec.rma_count = self.env['lgps.rma_process'].search_count([('device_id', '=', rec.id)])
