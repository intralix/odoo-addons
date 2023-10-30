from odoo import fields, models, api,_
import re
import logging
_logger = logging.getLogger(__name__)


class LgpsStocking(models.Model):
    _inherit = 'stock.picking'

    def action_update_device_sale_order(self):
        lines = self.move_line_ids
        devices_to_look_for = []

        for line in lines:
            if re.search('rastreo', line.product_id.name, re.IGNORECASE):
                # _logger.warning('Product: %s', line.product_id.name)
                # _logger.warning('Serial: %s', line.lot_id.name)
                devices_to_look_for.append(line.lot_id.name)

        if devices_to_look_for:
            self.write_so_in_ids(devices_to_look_for)

    def write_so_in_ids(self, devices_to_look_for):

        # _logger.warning('devices_to_look_for: %s', devices_to_look_for)
        sale_order = self.env['sale.order'].search([('name', '=', self.origin)])
        # _logger.warning('sale_order: %s', sale_order)
        if sale_order:
            devices = self.env['lgps.device'].search([('serial_number_id.name', 'in', devices_to_look_for)])
            devices.write({'sales_order_id': sale_order.id})
        # _logger.warning('Devices found: %s', devices)
