# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError
import logging
import re

_logger = logging.getLogger(__name__)
TAG_RE = re.compile(r'<[^>]+>')


class CellchipWizard(models.TransientModel):
    _name = "lgps.cellchip_wizard"
    _description = "Cellchips Operations Wizard"

    def _default_cellchips(self):
        return self.env['lgps.cellchip'].browse(self._context.get('active_ids'))

    cellchips_ids = fields.Many2many(
        comodel_name='lgps.cellchip',
        string=_("Cellchips"),
        required=True,
        default=_default_cellchips,
    )

    deactivation_date = fields.Date(
        string=_("Deactivation Date"),
    )

    comment = fields.Text(
        string=_("Comments"),
    )

    def execute_operation(self):
        if len(self._context.get('active_ids')) < 1:
            raise UserError(_('Select at least one record.'))

        active_records = self.return_active_records()
        # Updating date
        active_records.write({
            'deactivation_date': self.deactivation_date,
            'to_deactivate': False
        })

        for record in active_records:
            comment = self.comment if self.comment else ''
            # log comment if necessary
            if comment != '':
                record.message_post(body=comment)

        return {}

    def return_active_records(self):
        active_model = self._context.get('active_model')
        active_records = self.env[active_model].browse(self._context.get('active_ids'))

        return active_records

    def log_to_channel(self, channel_id, channel_msn):

        if not channel_id:
            raise UserError(
                _('There is not configuration for default channel.\n Configure this in order to send the notification.')
            )
        else:
            channel_notifier = self.sudo().env['mail.channel'].search([('id', '=', channel_id)])
            channel_notifier.message_post(body=channel_msn, subtype='mail.mt_comment', partner_ids=[(4, self.env.uid)])

        return {}

