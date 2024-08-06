# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class FsmServicesTypeList(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'lgps.fsm_services_type_list'
    _description = 'Custom FSM Services Type List Module'
    _order = 'name asc'

    name = fields.Char(
        required=True,
        string=_("Service Type"),
    )

    short_code = fields.Char(
        required=True,
        string=_("Short Code"),
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

        return super(FsmServicesTypeList, self).copy(default)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The service type list name must be unique"),
    ]
