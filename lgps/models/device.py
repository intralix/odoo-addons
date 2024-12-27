# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, models, fields, _
import math


class Device(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'lgps.device'
    _description = _('Gps Devices Module')
    _order = "name, id"

    @api.model
    def _default_stage_id(self):
        stage = self.env["lgps.device_stage"]
        return stage.search([
            ("state", "=", "ready_to_install")
        ], limit=1)

    @api.model
    def _group_expand_stage_id(self, stages, domain, order):
        return stages.search([], order=order)

    name = fields.Char(
        required=True,
        string=_("GPS Device"),
    )

    nick = fields.Char(
        string=_("Nick"),
    )

    imei = fields.Char(
        string=_("IMEI"),
    )

    idf = fields.Char(
        string=_("IDF"),
    )

    installation_date = fields.Date(
        string=_("Installation Date"),
    )

    warranty_start_date = fields.Date(
        string=_("Warranty Start Date"),
    )

    warranty_end_date = fields.Date(
        compute="_compute_end_warranty",
        string=_("Warranty End Date"),
        store=True,
    )

    warranty_term = fields.Selection(
        selection=[
            ("12", _("12 months")),
            ("18", _("18 months")),
            ("24", _("24 months")),
            ("36", _("36 months"))
        ],
        default="12",
        string=_("Warranty Term"),
    )

    tracking = fields.Boolean(
        default=False,
        string=_("Tracking"),
        tracking=True
    )

    fuel = fields.Boolean(
        default=False,
        string=_("Fuel"),
        tracking=True
    )

    fleetrun = fields.Boolean(
        default=False,
        string=_("Fleetrun"),
        tracking=True
    )

    speaker = fields.Boolean(
        default=False,
        string=_("Speaker"),
    )

    anti_jammer_blocker = fields.Boolean(
        default=False,
        string=_("Anti Jammer Blocker"),
    )

    smart_blocker = fields.Boolean(
        default=False,
        string=_("Smart Blocker"),
    )

    blocker = fields.Boolean(
        default=False,
        string=_("Blocker"),
    )

    scanner = fields.Boolean(
        default=False,
        string="Scanner",
        tracking=True
    )

    padlock = fields.Boolean(
        default=False,
        string=_("Padlock"),
    )

    solar_panel = fields.Boolean(
        default=False,
        string=_("Solar Panel"),
    )

    temperature = fields.Boolean(
        default=False,
        string=_("Temperature"),
        tracking=True
    )

    ibutton = fields.Boolean(
        default=False,
        string=_("iButton"),
    )

    microphone = fields.Boolean(
        default=False,
        string=_("Microphone"),
    )

    sheet = fields.Boolean(
        default=False,
        string=_("Sheet"),
    )

    opening_sensor = fields.Boolean(
        default=False,
        string=_("Opening Sensor"),
    )

    logistic = fields.Boolean(
        default=False,
        string=_("Logistic"),
        tracking=True
    )

    collective = fields.Boolean(
        default=False,
        string=_("Collective"),
        tracking=True
    )

    fuel_hall = fields.Boolean(
        default=False,
        string=_("Efecto Hall"),
        tracking=True
    )

    disengagement_sensor = fields.Boolean(
        default=False,
        string=_("Disengagement Sensor"),
    )

    datetime_gps = fields.Datetime(
        string=_("DateTime GPS"),
    )

    datetime_server = fields.Datetime(
        string=_("DateTime Server"),
    )

    last_position = fields.Char(
        string=_("Last Position"),
    )

    last_report = fields.Integer(
        string=_("Last Report"),
        compute="_compute_last_report",
        store=True,
        help="Time without reporting in platforms expressed in hours",
    )

    administrative_status = fields.Selection(
        selection=[
            ("drop", _("Drop")),
            ("comodato", _("Comodato")),
            ("courtesy", _("Courtesy")),
            ("demo", _("Demo")),
            ("external", _("External")),
            ("inventory", _("Inventory")),
            ("foreign_inventory", _("Foreing Inventory")),
            ("borrowed", _("Borrowed")),
            ("replacement", _("Replacement")),
            ("backup", _("Backup")),
            ("rma", _("RMA")),
            ("sold", _("Sold")),
            ("subscription", _("Subscription")),
            ("drop", _("Drop")),
            ("uninstalled", _("Uninstalled")),
            ("hibernate", _("Hibernate")),
            ("installed", _("Installed")),
            ("inventory", _("Inventory")),
            ("new", _("New")),
            ("for installing", _("For Installing")),
            ("tests", _("Tests")),
        ],
        default="inventory",
        string=_("Administrative Status"),
        tracking=True
    )

    platform_list_id = fields.Many2one(
        comodel_name="lgps.platform_list",
        string=_("Platform List"),
        ondelete="set null",
        index=True,
        domain=[('active', '=', True)],
        tracking=True,
    )

    product_id = fields.Many2one(
        comodel_name="product.product",
        required=True,
        string=_("Product Type"),
        index=True,
    )

    invoice_id = fields.Char(
        string=_("Provider Invoice"),
        index=True,
    )

    client_id = fields.Many2one(
        comodel_name="res.partner",
        required=True,
        string=_("Belongs To"),
        domain=[
            ('active', '=', True),
            ('is_company', '=', True)
        ],
        index=True,
        tracking=True
    )

    serial_number_id = fields.Many2one(
        comodel_name="stock.lot",
        required=False,
        string=_("Serial Number"),
        index=True,
    )

    historic_serial_number = fields.Char(
        required=False,
        string=_("Historic Serial Number"),
    )

    stage_id = fields.Many2one(
        "lgps.device_stage",
        default=_default_stage_id,
        group_expand="_group_expand_stage_id",
        tracking=True
    )

    state = fields.Selection(
        related="stage_id.state",
        store=True,
        string=_("Operative Status")
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

    purchase_date = fields.Date(
        default=fields.Date.today,
        string=_("Purchase Date"),
    )

    fuel_tank_type_one_id = fields.Many2one(
        comodel_name="product.product",
        string=_("Fuel Tank One"),
        tracking=True,
        domain=[('active', '=', True),
                '|', '|',
                ('default_code', 'like', 'ACCFEH%'),
                ('default_code', 'like', 'ACCFEL%'),
                ('default_code', 'like', 'ACCFLOP%')]
    )

    fuel_tank_type_two_id = fields.Many2one(
        comodel_name="product.product",
        string=_("Fuel Tank Two"),
        tracking=True,
        domain=[('active', '=', True),
                '|', '|',
                ('default_code', 'like', 'ACCFEH%'),
                ('default_code', 'like', 'ACCFEL%'),
                ('default_code', 'like', 'ACCFLOP%')]
    )

    fuel_tank_type_three_id = fields.Many2one(
        comodel_name="product.product",
        string=_("Fuel Tank Three"),
        tracking=True,
        domain=[('active', '=', True),
                '|', '|',
                ('default_code', 'like', 'ACCFEH%'),
                ('default_code', 'like', 'ACCFEL%'),
                ('default_code', 'like', 'ACCFLOP%')]
    )

    device_pin = fields.Char(
        string=_("Device PIN"),
    )

    electronics = fields.Boolean(
        default=False,
        string=_("Electronics"),
        tracking=True
    )

    sales_order_id = fields.Many2one(
        comodel_name="sale.order",
        ondelete="set null",
        string=_("Parent Sale Order"),
        help=_("Related Sales Order"),
        index=True,
        tracking=True,
    )

    vehicle_id = fields.Many2one(
        comodel_name="lgps.vehicle",
        ondelete="set null",
        string=_("Installed On"),
        help=_("Vehicle where this device is installed"),
        index=True,
        tracking=True,
    )

    cell_chip_id = fields.Many2one(
        comodel_name="lgps.cellchip",
        string=_("Cellchip Number"),
        ondelete='set null',
        required=False,
        tracking=True
    )

    accessory_ids = fields.One2many(
        comodel_name="lgps.accessory",
        inverse_name="device_id",
        string=_("Accessories"),
    )

    helpdesk_tickets_ids = fields.One2many(
        comodel_name="helpdesk.ticket",
        inverse_name="device_id",
        string=_("Tickets"),
    )

    fsm_ids = fields.One2many(
        comodel_name="project.task",
        inverse_name="device_id",
        string=_("Field Services"),
    )

    helpdesk_tickets_count = fields.Integer(
        string=_("Tickets Count"),
        compute='_compute_tickets_count',
        default=0
    )

    subscriptions_count = fields.Integer(
        string=_("Subscriptions Count"),
        compute='_compute_subscriptions_count',
        default=0
    )

    tracking_count = fields.Integer(
        string=_("Trackings Count"),
        compute='_compute_tracking_count',
        default=0
    )

    fsm_ids_count = fields.Integer(
        string=_("Services Count"),
        compute='_compute_fsm_count',
        default=0
    )

    odoo_version = fields.Selection(
        selection=[
            ("12", _("Odoo v12")),
            ("15", _("Odoo v15")),
            ("17", _("Odoo v17")),
        ],
        default="17",
        string=_("Odoo Version"),
    )

    def action_counter_tickets_button(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('helpdesk.helpdesk_ticket_action_main_my')
        action['context'] = {
            'default_device_id':  self.id,
            'default_partner_id': self.client_id
        }
        action['domain'] = [('device_id', '=', self.id)]
        return action

    def action_counter_subscription_button(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('sale_subscription.sale_subscription_action')
        action['context'] = {
            'default_device_id':  self.id,
            'default_partner_id': self.client_id.id
        }
        action['domain'] = [('device_id', '=', self.id)]
        return action

    def action_counter_tracking_button(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('lgps.tracking_list_action')
        action['context'] = {
            'default_device_id':  self.id,
            'default_client_id': self.client_id.id
        }
        action['domain'] = [('device_id', '=', self.id)]
        return action

    def action_counter_fsm_button(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('industry_fsm.project_task_action_fsm')
        default_project = self.env.ref('industry_fsm.fsm_project')

        action['context'] = {
            'default_device_id':  self.id,
            'default_partner_id': self.client_id.id,
            'default_project_id': default_project.id,
            'default_is_fsm': True,
            'default_fsm_mode': True,
        }
        action['domain'] = [('device_id', '=', self.id)]
        return action

    @api.model
    @api.depends('datetime_gps')
    def _compute_last_report(self):
        if not self.datetime_gps:
            self.last_report = None
        else:
            start_dt = fields.Datetime.from_string(self.datetime_gps)
            today_dt = fields.Datetime.from_string(fields.Datetime.now())
            difference = today_dt - start_dt
            time_difference_in_hours = difference.total_seconds() / 3600
            self.last_report = math.ceil(time_difference_in_hours)

    @api.model
    @api.depends('warranty_term', 'warranty_start_date')
    def _compute_end_warranty(self):
        if not (self.warranty_term and self.warranty_start_date):
            self.warranty_end_date = None
        else:
            months = int(self.warranty_term[:2])
            start = fields.Date.from_string(self.warranty_start_date)
            self.warranty_end_date = start + timedelta(months * 365 / 12)

    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', '=like', u"Copy of {}%".format(self.name))])
        if not copied_count:
            new_name = u"Copy of {}".format(self.name)
        else:
            new_name = u"Copy of {} ({})".format(self.name, copied_count)

        default['name'] = new_name

        return super(Device, self).copy(default)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The gps device id must be unique"),
    ]

    def _compute_tickets_count(self):
        for rec in self:
            rec.helpdesk_tickets_count = self.env['helpdesk.ticket'].search_count([('device_id', '=', rec.id)])

    def _compute_subscriptions_count(self):
        for rec in self:
            rec.subscriptions_count = self.env['sale.order'].search_count([('device_id', '=', rec.id)])

    def _compute_tracking_count(self):
        for rec in self:
            rec.tracking_count = self.env['lgps.tracking'].search_count([('device_id', '=', rec.id)])

    def _compute_fsm_count(self):
        for rec in self:
            rec.fsm_ids_count = self.env['project.task'].search_count([('device_id', '=', rec.id)])
