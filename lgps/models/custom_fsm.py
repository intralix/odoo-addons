from odoo import api, models, fields, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
import re


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

    has_material_picking_done = fields.Boolean(
        default=False,
        string=_("Picking already created"),
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

    def button_create_stock_picking(self):
        self.ensure_one()
        remove = re.compile('<.*?>')
        config = self.sudo().env['ir.config_parameter']
        move_ids_without_package = []
        default_operation = config.get_param('lgps.default_fsm_operation')
        active_record = self

        if not default_operation:
            raise UserError(
                _('Debes configurar una operación para enviar el material al almacén de revisión correctamente')
            )

        if active_record.has_material_picking_done:
            raise UserError(
                _('Ya se generó un movimiento de traslado de matrial para esta orden de servicio')
            )

        default_operation = self.sudo().env['stock.picking.type'].search([
            ('id', '=', default_operation)
        ])
        stock_picking = self.env['stock.picking']
        stock_picking_values = {
            'partner_id': int(active_record.partner_id.id),
            'picking_type_id': int(default_operation.id),
            'location_id': default_operation.default_location_src_id.id,
            'location_dest_id': default_operation.default_location_dest_id.id,
            'origin': active_record.name,
            'move_type': 'direct',
        }

        # En este punto creamos el Pick
        stock_picking_id = stock_picking.create(stock_picking_values)
        active_record.write({
            'stock_picking_id': stock_picking_id.id,
            'has_uninstalled_material': True,
            'has_material_picking_done': True,
        })

        # En este punto creamos los movimientos asociados al Pick recién creado
        for line in active_record.fsm_material_ids:
            temp = {
                'product_id': int(line.product_id.id),
                'product_uom_qty': int(1),
                'name': line.product_id.display_name,
                'description_picking': re.sub(remove, '', line.product_id.description),
                'product_uom': line.product_id.uom_id.id,
                'location_id': default_operation.default_location_src_id.id,
                'location_dest_id': default_operation.default_location_dest_id.id,
            }
            move_ids_without_package.append((0, 0, temp))
        # Escribimos la relación
        stock_picking_id.write({
            'move_ids_without_package': move_ids_without_package
        })
        stock_picking_id.action_confirm()

        # Para cada movimiento vamos a asociar el Número de Serie que indicó el instalador
        for line in stock_picking_id.move_line_ids_without_package:
            # _logger.warning('Linea a completar · de Serie: %s', line)
            # Buscamos en la información ingresada el dato correspondiente con la línea actual
            r = active_record.fsm_material_ids.search([('product_id', '=', line.product_id.id)], limit=1)

            if r and r.lot_id:
                _logger.error('Registro correspondiente de los ingresado: %s', r)
                _logger.info('lot_id seteado: %s', r.lot_id)
                line.write({'lot_id': r.lot_id.id})

        return True

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
