# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class AccessoryHistory(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'lgps.accessory_history'
    _description = 'Intx Accessories logs Internal Module'

    name = fields.Char(
        required=True,
        string=_("Internal Id"),
        default="Autogenerated on Save",
    )

    serial_number_id = fields.Many2one(
        comodel_name="stock.production.lot",
        string=_("Serial Number"),
    )

    client_id = fields.Many2one(
        comodel_name="res.partner",
        string=_("Client"),
        domain=[
            ('customer', '=', True),
            ('active', '=', True),
            ('is_company', '=', True)
        ],
    )

    accessory_ids = fields.Many2one(
        comodel_name='lgps.accessory',
        string="Gps Device",
        required=True,
    )

    destination_accessory_ids = fields.Many2one(
        comodel_name='lgps.accessory',
        string="Substitute equipment",
    )

    product_id = fields.Many2one(
        comodel_name="product.product",
        string=_("Product Type"),
    )
    operation_mode = fields.Selection(
        [
            ('replacement', _('Reemplazo de Equipo')),
            ('substitution', _('Sustitución de equipo por revisión')),
        ],
        default='drop',
    )

    related_odt = fields.Many2one(
        comodel_name='repair.order',
        string=_("Work order related"),
    )

    requested_by = fields.Char(
        string=_("Requested by"),
    )

    comment = fields.Text(
        string=_("Operation Reason"),
    )

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('lgps.accessory_history') or _('New')
        vals['name'] = seq
        return super(AccessoryHistory, self).create(vals)

    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', '=like', u"Copy of {}%".format(self.name))])
        if not copied_count:
            new_name = u"Copy of {}".format(self.name)
        else:
            new_name = u"Copy of {} ({})".format(self.name, copied_count)

        default['name'] = new_name
        return super(AccessoryHistory, self).copy(default)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The accessory id must be unique"),
    ]
