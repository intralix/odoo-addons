# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
import logging
_logger = logging.getLogger(__name__)


class AssignAccessoriesWizard(models.TransientModel):
    _name = "lgps.install_vehicle_wizard"
    _description = _("Add Installed devices to Vehicles")

    def _default_vehicles(self):
        return self.env['lgps.vehicle'].browse(self._context.get('active_ids'))

    vehicle_ids = fields.Many2many(
        comodel_name='lgps.vehicle',
        string=_("Vehicle"),
        required=True,
        default=_default_vehicles,
    )

    device_ids = fields.Many2many(
        comodel_name='lgps.device',
        string=_("Devices")
    )

    accessory_ids = fields.Many2many(
        comodel_name='lgps.accessory',
        string=_("Accessories")
    )

    def assign(self):
        _logger.warning('device_ids: %s', self.device_ids)
        today = fields.Date.today()

        for vehicle in self.vehicle_ids:
            vehicle.device_ids |= self.device_ids
            vehicle.accessory_ids |= self.accessory_ids

        # for accessory in self.accessory_ids:
        #     _logger.warning('accessory: %s', accessory)
        #     accessory.write({
        #         'installation_date': today,
        #         'status': 'installed',
        #         'last_assign_date': today
        #     })
        #
        #     if accessory.device_id.name:
        #         equipo = accessory.device_id.name
        #     else:
        #         equipo = "No identificado"
        #
        #     link_to_device = self._get_html_link(title=equipo)
        #
        #     accessory.message_post(body="Accesorio asignado el día: " + today.strftime('%d-%m-%Y')
        #                                 + " al dispositivo (" + link_to_device + ")",
        #                            body_is_html=True)

        return {}

