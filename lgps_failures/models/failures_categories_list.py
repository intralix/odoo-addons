# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class FailuresCategoriesList(models.Model):

    _name = 'lgps.failures_categories_list'
    _description = "Failures Categories list"
    _order = 'name asc'

    name = fields.Char(
        required=True,
        string=_("Failure Category"),
    )

    code = fields.Char(
        string=_("Internal Code"),
        readonly=True,
        required=True,
        copy=False,
        default='New'
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

        return super(FailuresCategoriesList, self).copy(default)

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('lgps.failures_categories_list') or _('New')
        vals['code'] = seq
        return super(FailuresCategoriesList, self).create(vals)
