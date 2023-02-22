from odoo import api, models, fields, _


class LgpsEmployee(models.Model):
    _inherit = 'hr.employee'

    curp = fields.Char(
        string=_("CURP"),
    )

    social_security_number = fields.Char(
        string=_("Security Social Number"),
    )
