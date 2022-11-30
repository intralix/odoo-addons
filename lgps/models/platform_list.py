# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
import logging
_logger = logging.getLogger(__name__)


class PlatformList(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'lgps.platform_list'
    _description = 'Intx Gps Devices Platforms List Module'

    name = fields.Char(
        required=True,
        string=_("Platform"),
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

        return super(PlatformList, self).copy(default)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The gps platform name must be unique"),
    ]
