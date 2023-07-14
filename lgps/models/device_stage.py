# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class DeviceStage(models.Model):
    _name = 'lgps.device_stage'
    _description = 'Device Stages model'
    _order = "sequence"

    name = fields.Char(
        required=True,
        string=_("Stage"),
    )

    sequence = fields.Integer(
        default=10
    )

    fold = fields.Boolean()

    active = fields.Boolean(default=True)

    state = fields.Selection([
        ('ready_to_install', _("Ready to Install")),
        ('installed', _("Installed")),
        ('replacement', _("Replacement")),
        ('hibernated', _("Hibernated")),
        ('asset_loan', _("Asset loan")),
        ('rma', _("RMA")),
        ('cancel', _("Canceled")),
        ('uninstalled', _("Uninstalled"))],
        default="inventory"
    )
