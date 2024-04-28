# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class DeviceStage(models.Model):
    _name = 'lgps.device_stage'
    _description = _('Device Stages model')
    _order = "sequence"

    name = fields.Char(
        required=True,
        string=_("Stage"),
    )

    sequence = fields.Integer(
        default=100
    )

    fold = fields.Boolean()

    active = fields.Boolean(default=True)

    state = fields.Selection([
        ('new', _("New")),
        ('ready_to_install', _("Ready to Install")),
        ('installed', _("Installed")),
        ('hibernated', _("Hibernated")),
        ('rma', _("RMA")),
        ('uninstalled', _("Uninstalled"))],
        default="ready_to_install"
    )
