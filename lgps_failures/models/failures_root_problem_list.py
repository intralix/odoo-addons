# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class FailuresRootProblemList(models.Model):

    _name = 'lgps.failure_root_problem_list'
    _description = _("Root Problems List")
    _order = "name asc"

    name = fields.Char(
        required=True,
        string=_("Root Problem"),
    )

    code = fields.Char(
        string=_("Internal Code"),
        readonly=True,
        required=True,
        copy=False,
        default='New'
    )

    invalidate = fields.Boolean(
        default=False,
        string=_("Voids Warranty"),
    )

    failures_list_ids = fields.Many2many(
        comodel_name="lgps.failures_list",
        string=_("Root Problems Applied to"),
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

        return super(FailuresRootProblemList, self).copy(default)

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('lgps.failure_root_problem_list') or _('New')
        vals['code'] = seq
        return super(FailuresRootProblemList, self).create(vals)
