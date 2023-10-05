from odoo import api, models, fields, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

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

    @api.model
    def create(self, values):
        if self._check_if_can_create():
            new_record = super(LgpsPartner, self).create(values)
        return new_record
    
    # def write(self, values):
    #    if self._check_if_can_create():
    #        return super(LgpsPartner, self).write(values)

    def _check_if_can_create(self):
        user = self.env.user
        if not user.has_group('lgps.lgps_group_create_contacts'):
            raise UserError('Solo personal de Administración y Finanzas puede dar alta de Clientes y Proveedores '
                            'nuevos.')
        return True
