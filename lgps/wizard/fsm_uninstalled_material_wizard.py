# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


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

        # if not active_record:
        #     raise UserError(_('No se ha encontrado nada en el contexto'))
        # else:
        #     raise UserError(_('active_records %s', active_record.partner_id.name))

        # if not self.stock_move_ids:
        #     raise UserError(
        #         _('No has registrado información')
        #     )
        #
        # lgps_config = self.sudo().env['ir.config_parameter']
        # default_operation = lgps_config.get_param('lgps.default_fsm_operation')
        #
        # if not default_operation:
        #     raise UserError(
        #         _('Debes configurar una operación para enviar el material al almacén virtual de revisión correctamente')
        #     )
        #
        # _logger.warning('default_operation: %s', default_operation)
        #
        # default_operation = self.sudo().env['stock.picking.type'].search([('id', '=', default_operation)])
        # _logger.warning('default_operation: %s', default_operation)
        #
        # stock_picking = self.env['stock.picking']
        # stock_picking_values = {
        #     'partner_id': int(active_record.partner_id.id),
        #     'picking_type_id': int(default_operation.id),
        #     'location_id': default_operation.default_location_src_id,
        #     'location_dest_id': default_operation.default_location_dest_id,
        #     'origin': active_record.name,
        #     'move_ids_without_package': []
        # }
        #
        # for line in self.stock_move_ids:
        #
        #     temp = {
        #         'product_id': int(line.product_id.id),
        #         'product_uom_quantity': int(1),
        #         'description_picking': line.product_id.display_name,
        #     }
        #     stock_picking_values['move_ids_without_package'].append((0, 0, temp))
        #
        # _logger.warning('stock_picking_values: %s', stock_picking_values)
        # stock_picking_id = stock_picking.create(stock_picking_values)
        # active_record.write({'stock_picking_id': stock_picking_id.id})
        #
        # _logger.warning('stock_picking created id: %s', stock_picking_id)

        return True
