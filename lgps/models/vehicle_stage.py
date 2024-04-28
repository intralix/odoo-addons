# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class VehicleStage(models.Model):
    _name = 'lgps.vehicle_stage'
    _description = 'Vehicle Stages model'
    _order = "sequence"

    name = fields.Char(
        required=True,
        string=_("Vehicle Stage"),
    )

    sequence = fields.Integer(
        default=10
    )

    fold = fields.Boolean()

    active = fields.Boolean(default=True)

    state = fields.Selection([
        ('active', _("Active")),
        ('inactive', _("Inactive")),
        ('in_maintenance', _("In Maintenance")),
        ('damaged', _("Damaged"))],
        default="active"
    )
