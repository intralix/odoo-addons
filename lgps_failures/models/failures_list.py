# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class FailuresList(models.Model):

    _name = 'lgps.failures_list'
    _description = "Failures list"

    name = fields.Char(
        required=True,
        string=_("Failure"),
    )

    code = fields.Char(
        string=_("Internal Code"),
        readonly=True,
        required=True,
        copy=False,
        default='New'
    )

    restricted = fields.Boolean(
        string=_("Restricted Option"),
        default=False
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

        return super(FailuresList, self).copy(default)

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('lgps.failures_list') or _('New')
        vals['code'] = seq
        return super(FailuresList, self).create(vals)
