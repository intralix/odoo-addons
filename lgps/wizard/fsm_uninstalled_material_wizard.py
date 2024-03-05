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

        # for line in self.stock_move_ids:
        #     _logger.warning('self.stock_move_ids: %s', line)
        #     r = self.stock_move_ids.search([
        #         ('name', '=', line.name),
        #         ('product_id', '=', line.product_id.id)
        #          ], limit=1)
        #     # r = self.stock_move_ids.name_search(name=line.name, args=None, operator='ilike', limit=1)
        #     _logger.error('searched thing: %s', r)

        # TODO : Revisar si es necesario primero crear cada registro del mòdulo stock.move y luego relacionar
        # al registro de stock.picking

        # if not active_record:
        #     raise UserError(_('No se ha encontrado nada en el contexto'))
        # else:
        #     raise UserError(_('active_records %s', active_record.partner_id.name))
        #
        _logger.warning('self.stock_move_ids: %s', self.stock_move_ids)
        # if not self.stock_move_ids:
        #     raise UserError(
        #         _('No has registrado información')
        #     )
        # raise UserError(_('Something here should stop'))

        lgps_config = self.sudo().env['ir.config_parameter']
        default_operation = lgps_config.get_param('lgps.default_fsm_operation')

        if not default_operation:
            raise UserError(
                _('Debes configurar una operación para enviar el material al almacén virtual de revisión correctamente')
            )

        _logger.warning('default_operation: %s', default_operation)

        default_operation = self.sudo().env['stock.picking.type'].search([('id', '=', default_operation)])
        # _logger.warning('default_operation: %s', default_operation)
        # _logger.warning('default_location_src_id: %s', default_operation.default_location_src_id)
        # _logger.warning('default_location_dest_id: %s', default_operation.default_location_dest_id)

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
        active_record.write({'stock_picking_id': stock_picking_id.id})

        move_ids_without_package = []
        remove = re.compile('<.*?>')

        # En este punto creamos los movimientos asociados al Pick recién creado
        for line in self.stock_move_ids:
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
        stock_picking_id.write({'move_ids_without_package': move_ids_without_package})
        stock_picking_id.action_confirm()

        # Para cada movimiento vamos a asociar el Número de Serie que indicó el instalador
        for line in stock_picking_id.move_line_ids_without_package:
            _logger.warning('Linea a completar · de Serie: %s', line)
            # line.lot_id = self.stock_move_ids
            # Buscamos en la información ingresada el dato correspondiente con la línea actual
            r = self.stock_move_ids.search([('product_id', '=', line.product_id.id)], limit=1)

            if r and r.lot_id:
                _logger.error('Registro correspondiente de los ingresado: %s', r)
                _logger.info('lot_id seteado: %s', r.lot_id)
                line.write({'lot_id': r.lot_id.id})

        return True
