# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class AssignAccessoriesWizard(models.TransientModel):
    _name = "lgps.add_accessories_wizard"
    _description = "Add Accessories to Devices"

    def _default_gpsdevices(self):
        return self.env['lgps.device'].browse(self._context.get('active_ids'))

    gpsdevice_ids = fields.Many2many(
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
        for gpsdevice in self.gpsdevice_ids:
            gpsdevice.accessory_ids |= self.accessory_ids

        today = fields.Date.today()
        for accessory in self.accessory_ids:
            accessory.write({'installation_date': today, 'status': 'installed'})
            if accessory.device_id.name:
                equipo = accessory.device_id.name
            else:
                equipo = "No identificado"

            accessory.message_post(body="Accesorio asignado el día: " + today.strftime('%d-%m-%Y')
                                        + " al equipo [<strong>" + equipo + "</strong>]")

        return {}

