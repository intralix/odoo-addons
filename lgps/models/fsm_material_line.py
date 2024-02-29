# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class FsmMaterialLine(models.Model):
    _name = 'lgps.fsm_material_line'
    _description = 'Fsm Material Line (parts)'

    name = fields.Text('Description', required=True)

    project_task_id = fields.Many2one(
        comodel_name="project.task",
        string=_('Fsm Task'),
        required=True,
    )

    product_id = fields.Many2one(
        comodel_name="product.product",
        string=_('Product'),
        required=True,
        domain="[('type', 'in', ['product', 'consu']), ('tracking', 'in', ['serial','lot'])]")

    lot_id = fields.Many2one(
        comodel_name="stock.production.lot",
        string=_('Lot/Serial'),
        domain="[('product_id','=', product_id)]",
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        domain = {}
        if self.product_id:
            list_ids = []
            values = self.env['stock.production.lot'].search([('product_id', '=', self.product_id.id)])

            for value in values:
                list_ids.append(value.id)

            self.lot_id = []
            domain = {'lot_id': [('id', 'in', list_ids)]}

            return {'domain': domain}
