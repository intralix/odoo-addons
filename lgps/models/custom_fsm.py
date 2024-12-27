from odoo import api, models, fields, _
from odoo.exceptions import UserError
import json
import logging
_logger = logging.getLogger(__name__)
import re


class LgpsFSM(models.Model):
    _inherit = 'project.task'

    def _default_service_type_list(self):
        value = self.env['lgps.fsm_services_type_list'].search([('id', '=', 1)], limit=1).id
        if not value:
            value = None

        return value

    device_id = fields.Many2one(
        comodel_name="lgps.device",
        ondelete="set null",
        string=_("Device"),
        help="GPS Device associated with the service.",
        domain=[('administrative_status', 'in', [
            "comodato",
            "courtesy",
            "demo",
            "external",
            "hibernate",
            "installed",
            "inventory",
            "new",
            "for installing",
            "borrowed",
            "replacement",
            "backup",
        ])],
        index=True,
        tracking=True,
    )

    nick = fields.Char(
        string=_('Nick'),
        related="device_id.nick",
        store=True
    )

    service_type_list_id = fields.Many2one(
        comodel_name="lgps.fsm_services_type_list",
        string=_("Service Type List"),
        default=_default_service_type_list,
        ondelete="set null",
        index=True,
        domain=[('active', '=', True)],
        tracking=True,
    )

    show_timesheet_in_report = fields.Boolean(
        string=_("Show timesheet in Reports"),
        default=False
    )

    parent_sales_order_id = fields.Many2one(
        comodel_name="sale.order",
        ondelete="set null",
        string=_("Parent Sale Order"),
        help="Project Sales Order to work with",
        index=True,
        tracking=True,
    )

    vehicle_id = fields.Many2one(
        comodel_name="lgps.vehicle",
        ondelete="set null",
        string=_("Vehicle"),
        help="Vehicle associated with the service.",
        index=True,
        tracking=True,
    )

    fsm_material_ids = fields.One2many(
        comodel_name="lgps.fsm_material_line",
        inverse_name="project_task_id",
        string=_("Uninstalled Material"),
        index=True,
        tracking=True,
    )

    revisions_ids = fields.One2many(
        comodel_name="lgps.revision",
        inverse_name="project_task_id",
        string=_("Revisions"),
        index=True
    )

    stock_picking_id = fields.Many2one(
        comodel_name="stock.picking",
        string=_("Stock Moves"),
        ondelete="set null",
        index=True,
        tracking=True,
    )

    has_uninstalled_material = fields.Boolean(
        default=False,
        string=_("Has Uninstalled Material"),
    )

    has_material_picking_done = fields.Boolean(
        default=False,
        string=_("Picking already created"),
    )

    has_revisions_created = fields.Boolean(
        default=False,
        string=_("Revisions were already created"),
    )

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            short_code = 'SER'
            device_name = 'NA'
            today_dt = fields.Datetime.context_timestamp(self, fields.Datetime.now())
            if self.service_type_list_id:
                service = self.env['lgps.fsm_services_type_list'].search([['id', '=', values['service_type_list_id']]], limit=1)
                if service:
                    short_code = service.short_code

            if 'device_id' in values and values['device_id']:
                device = self.env['lgps.device'].search([['id', '=', values['device_id']]], limit=1)
                if device:
                    if device.nick:
                        device_name = device.nick
                    else:
                        device_name = device.name

            values['name'] = short_code + '/' + today_dt.strftime("%Y/%m/%d/%H%M") + '/' + device_name

            res = super(LgpsFSM, self).create(values)
        return res

    def open_uninstalled_material_wizard(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Removed Material'),
            'res_model': 'lgps.uninstalled_material_wizard',
            'target': 'new',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {'default_project_task_id': self.id}
        }
        return action

    def create_revisions_from_material_lines(self):
        created_revisions = []
        if not self.has_revisions_created:
            for rec in self.fsm_material_ids:
                new_revision = self.env['lgps.revision']

                temp = {
                    'observations': rec.observation,
                    'notes': '',
                    'project_task_id': int(rec.project_task_id.id),
                    'product_id': int(rec.product_id.id),
                    'lot_id': int(rec.lot_id.id),
                    'state': 'new',
                    'resolution': '',
                }

                revision = new_revision.create(temp)
                created_revisions.append(int(revision.id))

            self.write({
                'revisions_ids': [(6, 0, created_revisions)],
                'has_revisions_created': True,
            })

        else:
            raise UserError(
                _('Ya se han creado todas las revisiones de este servicio.')
            )
