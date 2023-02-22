from odoo import api, models, fields, _


class LgpsPartner(models.Model):
    _inherit = 'res.partner'

    client_type = fields.Selection(
        [
            ('new', _('New')),
            ('aftersales', _('After Sales')),
        ],
        default='new',
        string=_("Client Type")
    )

    first_installation_day = fields.Date(
        string=_("First Installation Day")
    )

    custom_status = fields.Selection(
        [
            ('active', _('Active')),
            ('cancelled', _('Cancelled')),
            ('demo', _('Demo')),
            ('inactive', _('Inactive')),
            ('suspended', _('Suspended')),
            ('on_negotiation', _('On Negotiation')),
            ('in_credit_bureau', _('In Credit Bureau')),
        ],
        default='active'
    )

    client_rank = fields.Selection(
        [
            ('a', 'A'),
            ('b', 'B'),
            ('c', 'C'),
            ('d', 'D'),
            ('e', 'E'),
        ],
        default='e',
        string=_("Client Rank")
    )

    coordination_executive = fields.Many2one(
        comodel_name="res.users",
        string=_("Coordination"),
        ondelete="set null",
    )

    credit_collection_executive = fields.Many2one(
        comodel_name="res.users",
        string=_("Credit and Collection"),
        ondelete="set null",
    )

    after_sales_executive = fields.Many2one(
        comodel_name="res.users",
        string=_("After Sales"),
        ondelete="set null",
    )

    special_negotiations = fields.Boolean(
        string=_("Special Negotiations"),
        default=False
    )

    special_negotiation_notes = fields.Html(
        string=_("Special Negotiations Notes")
    )

    gpsdevice_ids = fields.One2many(
        comodel_name="lgps.device",
        inverse_name="client_id",
        string="Gps Devices",
        readonly=True,
    )
