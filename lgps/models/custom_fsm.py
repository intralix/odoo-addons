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