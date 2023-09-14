from odoo import api, models, fields, _


class LgpsFSM(models.Model):
    _inherit = 'project.task'

    device_id = fields.Many2one(
        comodel_name="lgps.device",
        ondelete="set null",
        string=_("Device"),
        help="GPS Device associated with the service.",
        domain=[('status', 'in', [
            "comodato",
            "courtesy",
            "demo",
            "external",
            "hibernate",
            "installed",
            "inventory",
            "new",
            "for installing",
            "borrowed",
            "replacement",
            "backup",
        ])],
        index=True,
        tracking=True,
    )

    nick = fields.Char(
        string=_('Nick'),
        related="device_id.nick",
        store=True
    )

    show_timesheet_in_report = fields.Boolean(
        string=_("Show timesheet in Reports"),
        default=False
    )

    parent_sales_order_id = fields.Many2one(
        comodel_name="sale.order",
        ondelete="set null",
        string=_("Sale Order"),
        help="Project Sales Order to work with",
        index=True,
        tracking=True,
    )

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        domain = {}
        if self.partner_id:
            list_ids = []
            values = self.env['lgps.device'].search([('client_id', '=', self.partner_id.id)])

            for value in values:
                list_ids.append(value.id)

            self.device_id = []
            domain = {'device_id': [('id', 'in', list_ids)]}

            return {'domain': domain}

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s - %s' % (rec.name, rec.project_id.name)))

        return result
