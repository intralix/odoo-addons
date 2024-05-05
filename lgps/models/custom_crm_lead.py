from odoo import api, models, fields, _


class LgpsCrmLead(models.Model):
    _inherit = 'crm.lead'

    life_cycle_stage = fields.Selection([
        ('lead', "Lead"),
        ('replied', "Replied"),
        ('negative_reply', "Negative Reply"),
        ('follow_up', "Follow Up"),
        ('client', "Client"),
        ('bounce_spam', "Bounce/Spam"),
        ('lin', "LIN"),
        ('no_contact', "No Contact"),
    ],
        string=_('Life Cycle Stage'),
    )

    lin_connection = fields.Selection([
        ("sent", _("Sent")),
        ("accepted", _("Accepted")),
        ("on_campaign", _("On Campaing")),
        ("lead", _("Lead")),
        ("no_replied", _("No replied")),
    ],
        string=_("LIN Connection"),
    )

    lead_job_department = fields.Selection([
        ("finance", _("Finance")),
        ("legal", _("Legal")),
        ("security", _("Security")),
        ("ti", _("TI")),
        ("owner_ceo_founder", _("Owner/CEO/Founder")),
        ("ops", _("OPS")),
        ("maintenance", _("Maintenance")),
        ("quality", _("Quality")),
        ("fuel_mgmt", _("Fuel Mgmt")),
        ("administration", _("Administration")),
        ("general_mgmt", _("General Mgmt")),
        ("others", _("Others")),
    ])

    personal_email = fields.Char(
        string=_("Personal Email"),
    )

    mobile_two = fields.Char(
        string=_("Mobile 2"),
    )

    linked_in_profile = fields.Char(
        string=_("LinkedIn Profile"),
    )
