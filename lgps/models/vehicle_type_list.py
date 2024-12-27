# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class VehicleTypeList(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'lgps.vehicle_type'
    _description = _('Vehicles Type List Module')

    name = fields.Char(
        required=True,
        string=_("Vehicle Type"),
    )

    active = fields.Boolean(
        default=True
    )

    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', '=like', u"Copy of {}%".format(self.name))])
        if not copied_count:
            new_name = u"Copy of {}".format(self.name)
        else:
            new_name = u"Copy of {} ({})".format(self.name, copied_count)

        default['name'] = new_name

        return super(VehicleTypeList, self).copy(default)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The vehicle type name must be unique"),
    ]
