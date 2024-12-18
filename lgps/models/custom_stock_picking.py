from odoo import api, models, fields, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
import re


class LgpsStockPicking(models.Model):
    _inherit = 'stock.picking'

    def move_lines_to_virtual_location(self):

        self.ensure_one()
        remove = re.compile('<.*?>')
        config = self.sudo().env['ir.config_parameter']
        move_ids_without_package = []
        default_operation = config.get_param('lgps.virtual_default_location')
        default_operation = self.env['stock.picking.type'].search([['id', '=', default_operation]], limit=1)
        active_record = self

        _logger.error('default_operation: %s', default_operation)
        _logger.error('active_record: %s', active_record)
        _logger.error('return_id: %s', self.return_id)

        stock_move = self.env['stock.move'].search([['picking_id', '=', active_record.id]])
        stock_move_line = self.env['stock.move.line'].search([['picking_id', '=', active_record.id]])


        _logger.warning('active_record.move_ids_without_package: %s', active_record.move_ids_without_package)
        for record in active_record.stock_move:
            _logger.warning('record: %s', record)
            for line in record:
                _logger.warning('line: %s', line)



        # for line in stock_move_line:
        #     _logger.warning('line: %s', line)

        # stock_picking_values = {
        #     'partner_id': int(active_record.partner_id.id),
        #     'picking_type_id': int(default_operation.id),
        #     'location_id': default_operation.default_location_src_id.id,
        #     'location_dest_id': default_operation.default_location_dest_id.id,
        #     'origin': active_record.name,
        #     'move_type': 'direct',
        # }
        #
        # # stock_picking = self.env['stock.picking']
        # # stock_picking_id = stock_picking.create(stock_picking_values)
        # _logger.warning('stock_picking_values: %s', stock_picking_values)
        #
        #
        # for line in stock_move_line:
        #     _logger.warning('line: %s', line)
        #     temp = {
        #         'product_id': int(line.product_id.id),
        #         'product_uom_qty': line.quantity,
        #         'name': line.product_id.display_name,
        #         'description_picking': line.product_id.description,
        #         'product_uom_id': line.product_id.uom_id.id,
        #         'location_id': default_operation.default_location_src_id.id,
        #         'location_dest_id': default_operation.default_location_dest_id.id,
        #     }
        #     _logger.warning('stock_move_line: %s', temp)

            raise UserError('Stop Execution to debug this shit')

        # if not default_operation:
        #     raise UserError(
        #         _('Debes configurar una operación para enviar el material al almacén de revisión correctamente')
        #     )
        #
        #
        # # En este punto creamos el Pick
        # stock_picking_id = stock_picking.create(stock_picking_values)
        # active_record.write({
        #     'stock_picking_id': stock_picking_id.id,
        #     'has_uninstalled_material': True,
        #     'has_material_picking_done': True,
        # })
        #
        # # En este punto creamos los movimientos asociados al Pick recién creado
        # for line in active_record.fsm_material_ids:
        #     temp = {
        #         'product_id': int(line.product_id.id),
        #         'product_uom_qty': int(1),
        #         'name': line.product_id.display_name,
        #         'description_picking': re.sub(remove, '', line.product_id.description),
        #         'product_uom': line.product_id.uom_id.id,
        #         'location_id': default_operation.default_location_src_id.id,
        #         'location_dest_id': default_operation.default_location_dest_id.id,
        #     }
        #     move_ids_without_package.append((0, 0, temp))
        # # Escribimos la relación
        # stock_picking_id.write({
        #     'move_ids_without_package': move_ids_without_package
        # })
        # stock_picking_id.action_confirm()
        #
        # # Para cada movimiento vamos a asociar el Número de Serie que indicó el instalador
        # for line in stock_picking_id.move_line_ids_without_package:
        #     # _logger.warning('Linea a completar · de Serie: %s', line)
        #     # Buscamos en la información ingresada el dato correspondiente con la línea actual
        #     r = active_record.fsm_material_ids.search([('product_id', '=', line.product_id.id)], limit=1)
        #
        #     if r and r.lot_id:
        #         _logger.error('Registro correspondiente de los ingresado: %s', r)
        #         _logger.info('lot_id seteado: %s', r.lot_id)
        #         line.write({'lot_id': r.lot_id.id})

        return True
