from odoo import api, models, fields, _


class CustomHelDesk(models.Model):
    _inherit = 'helpdesk.ticket'

    device_id = fields.Many2one(
        comodel_name="lgps.device",
        string=_("Gps Device"),
        ondelete="set null",
        index=True,
    )
