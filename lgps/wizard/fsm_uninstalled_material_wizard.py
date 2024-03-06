# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
import re


class UninstalledMaterialWizard(models.TransientModel):
    _name = "lgps.uninstalled_material_wizard"
    _description = _("Report uninstalled material in fsm")

    stock_move_ids = fields.Many2many(
        comodel_name='lgps.fsm_material_line',
        string=_("Uninstalled Material")
    )

    def button_process(self):
        self.ensure_one()

        active_model = self._context.get('active_model')
        active_record = self.env[active_model].browse(self._context.get('active_ids'))

        active_record.write({
            'has_uninstalled_material': True
        })

        return True
