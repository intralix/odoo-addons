from odoo import api, models, fields, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class LgpsFSM(models.Model):
    _inherit = 'project.task'

    # def _default_service_type_list(self):
    #     return self.env['lgps.fsm_services_type_list'].search([('id', '=', 1)], limit=1).id

    device_id = fields.Many2one(
        comodel_name="lgps.device",
        ondelete="set null",
        string=_("Device"),
        help="GPS Device associated with the service.",
        domain=[('status', 'in', [
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

    is_warranty = fields.Boolean(
        string=_("It's Warranty"),
        default=False
    )

    guarantee_justification = fields.Html(
        string=_("Guarantee Justification"),
    )

    warranty_list_id = fields.Many2one(
        comodel_name="lgps.fsm_warranties_list",
        string=_("Warranty Reason List"),
        ondelete="set null",
        index=True,
        domain=[('active', '=', True)],
        tracking=True,
    )

    repair_id = fields.Many2one(
        comodel_name="repair.order",
        ondelete="set null",
        string=_("Repair Order"),
        help=_("When a product it's about treated as warranty, it must have a repair order process associated."),
        index=True,
        tracking=True,
    )

    service_type_list_id = fields.Many2one(
        comodel_name="lgps.fsm_services_type_list",
        string=_("Service Type List"),
        # default=_default_service_type_list,
        ondelete="set null",
        index=True,
        domain=[('active', '=', True)],
        tracking=True,
    )

    fsm_material_ids = fields.One2many(
        comodel_name="lgps.fsm_material_line",
        inverse_name="project_task_id",
        string=_("Uninstalled Material"),
        index=True,
        tracking=True,
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

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        domain = {}
        if self.partner_id:
            list_ids = []
            values = self.env['lgps.device'].search([('client_id', '=', self.partner_id.id)])

            for value in values:
                list_ids.append(value.id)

            self.device_id = []
            domain = {'device_id': [('id', 'in', list_ids)]}

            return {'domain': domain}

    @api.model
    def create(self, values):
        short_code = 'SER'
        device_name = 'NA'
        today_dt = fields.Datetime.context_timestamp(self, fields.Datetime.now())
        service = self.env['lgps.fsm_services_type_list'].search([['id', '=', values['service_type_list_id']]], limit=1)
        if service:
            short_code = service.short_code

        # if 'name' in values and values['name']:
        if 'device_id' in values and values['device_id']:
            device = self.env['lgps.device'].search([['id', '=', values['device_id']]], limit=1)
            if device:
                if device.nick:
                    device_name = device.nick
                else:
                    device_name = device.name

        values['name'] = short_code + '/' + device_name + '/' + today_dt.strftime("%Y/%m/%d%H%M")

        res = super(LgpsFSM, self).create(values)
        # here you can do accordingly
        return res
