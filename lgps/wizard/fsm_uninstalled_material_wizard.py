# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class UninstalledMaterialWizard(models.TransientModel):
    _name = "lgps.uninstalled_material_wizard"
    _description = _("Report uninstalled material in fsm")

    def _default_project_task(self):
        return self.env['project.task'].browse(self._context.get('active_ids'))

    stock_move_ids = fields.Many2many(
        comodel_name='lgps.fsm_material_line',
        string=_("Uninstalled Material"),
    )

    project_task_id = fields.Many2one(
        comodel_name='project.task',
        string=_("Project Task"),
        default=_default_project_task,
    )

    def button_process(self):
        self.ensure_one()

        active_model = self._context.get('active_model')
        active_record = self.env[active_model].browse(self._context.get('active_ids'))

        active_record.write({
            'has_uninstalled_material': True
        })

        return True
