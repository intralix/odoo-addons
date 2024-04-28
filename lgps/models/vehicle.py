# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class Vehicle(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'lgps.vehicle'
    _description = 'Intx Vehicles Module'

    @api.model
    def _default_stage_id(self):
        stage = self.env["lgps.vehicle_stage"]
        return stage.search([
            ("state", "=", "active")
        ], limit=1)

    @api.model
    def _group_expand_stage_id(self, stages, domain, order):
        return stages.search([], order=order)

    name = fields.Char(
        required=True,
        string=_("Vehicle Nick"),
    )

    year = fields.Char(
        string=_("Vehicle Year"),
    )

    serial_number = fields.Char(
        string=_("Serial Number"),
    )

    brand = fields.Char(
        string=_("Brand"),
    )

    model = fields.Char(
        string=_("Model"),
    )

    vehicle_color = fields.Char(
        string=_("Vehicle Color"),
    )

    plates = fields.Char(
        string=_("Plates"),
    )

    fuel_performance = fields.Float(
        string=_("Fuel Performance"),
    )

    vehicle_type_id = fields.Many2one(
        comodel_name="lgps.vehicle_type",
        string=_("Vehicle Type"),
        ondelete="set null",
        index=True,
        domain=[('active', '=', True)],
        tracking=True,
    )

    client_id = fields.Many2one(
        comodel_name="res.partner",
        required=True,
        string=_("Client"),
        domain=[
            ('active', '=', True),
            ('is_company', '=', True)
        ],
        index=True,
        tracking=True
    )

    stage_id = fields.Many2one(
        "lgps.vehicle_stage",
        default=_default_stage_id,
        group_expand="_group_expand_stage_id",
        tracking=True
    )

    state = fields.Selection(
        related="stage_id.state",
        store=True,
        string=_("Vehicle Status")
    )

    kanban_state = fields.Selection([
        ("normal", "In Progress"),
        ("blocked", "Blocked"),
        ("done", "Ready for next stage")],
        "Kanban State",
        default="normal"
    )

    color = fields.Integer()

    priority = fields.Selection([
        ('0', "Normal"),
        ('1', "Medium"),
        ('2', "High"),
        ('3', "Critical")],
        string='Priority',
        default='0'
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

        return super(Vehicle, self).copy(default)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The vehicle id must be unique"),
    ]
