# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
import logging
_logger = logging.getLogger(__name__)


class AssignAccessoriesWizard(models.TransientModel):
    _name = "lgps.add_accessories_wizard"
    _description = _("Add Accessories to Devices")

    def _default_gpsdevices(self):
        return self.env['lgps.device'].browse(self._context.get('active_ids'))

    device_ids = fields.Many2many(
        comodel_name='lgps.device',
        string=_("Gps Device"),
        required=True,
        default=_default_gpsdevices,
    )

    accessory_ids = fields.Many2many(
        comodel_name='lgps.accessory',
        string=_("Accessories")
    )

    def assign(self):
        _logger.warning('device_ids: %s', self.device_ids)

        for device_ids in self.device_ids:
            _logger.warning('device_ids.accessory_ids: %s', device_ids.accessory_ids)
            device_ids.accessory_ids |= self.accessory_ids
            _logger.warning('device_ids.accessory_ids: %s', device_ids.accessory_ids)

        today = fields.Date.today()
        for accessory in self.accessory_ids:
            _logger.warning('accessory: %s', accessory)
            accessory.write({
                'installation_date': today,
                'status': 'installed',
                'last_assign_date': today
            })

            if accessory.device_id.name:
                equipo = accessory.device_id.name
            else:
                equipo = "No identificado"

            link_to_device = self._get_html_link(title=equipo)

            accessory.message_post(body="Accesorio asignado el día: " + today.strftime('%d-%m-%Y')
                                        + " al dispositivo (" + link_to_device + ")",
                                   body_is_html=True)

        return {}

