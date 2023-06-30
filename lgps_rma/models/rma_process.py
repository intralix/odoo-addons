# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class RmaProcess(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'lgps.rma_process'
    _description = 'Intx RMA Tracking for Gps Devices'

    name = fields.Char(
        required=True,
        string=_("Internal Id"),
        default="Autogenerated on Save",
    )
    state = fields.Selection(
        [
            ('reception', _('Reception')),
            ('shipment_to_supplier', _('Shipment to Supplier')),
            ('delivery_to_customer', _('Delivery to Customer')),
            ('done', _('Done'))
        ],
        index=True,
        readonly=True,
        default='reception',
        tracking=True
    )

    assigned_to = fields.Many2one(
        required=True,
        comodel_name="hr.employee",
        string=_("Assigned To"),
    )

    client_id = fields.Many2one(
        required=True,
        comodel_name="res.partner",
        string=_("Client"),
        domain=[
            ('is_company', '=', True)
        ],
    )

    device_id = fields.Many2one(
        comodel_name="lgps.device",
        string=_("Gps Device"),
        ondelete="set null",
        index=True,
    )

    accessories_id = fields.Many2one(
        comodel_name='lgps.accessory',
        ondelete="set null",
        index=True,
    )

    delivery_responsible = fields.Many2one(
        required=True,
        comodel_name="hr.employee",
        string=_("Delivery Responsible"),
    )

    problem = fields.Text(
        string=_("Fail")
    )

    diagnostic = fields.Text(
        string=_("Diagnostic")
    )

    shipped_date = fields.Date(
        string=_("Shipped date")
    )

    track_number = fields.Char(
        string=_("Track Number")
    )
    provider_reference = fields.Char(
        string=_("Provider Reference")
    )
    return_date = fields.Date()

    observations = fields.Text(
        string=_("Observations")
    )

    provider = fields.Selection(
        selection=[
            ("boson", "Boson"),
            ("logica_mobile", "Logica Mobile"),
        ],
        string=_("Provider"),
        tracking=True
    )

    apply_to = fields.Selection(
        selection=[
            ("gps_devices", _("Gps Devices")),
            ("accessories", _("Accessories")),
        ],
        default="gps_devices",
        string=_("Apply To")
    )

    coordinator = fields.Many2one(
        required=False,
        comodel_name="res.users",
        string=_("Coordinator"),
    )

    assistant = fields.Many2one(
        comodel_name="hr.employee",
        string=_("Assistant A"),
    )

    @api.model
    def create(self, values):
        seq = self.env['ir.sequence'].next_by_code('lgps.rma_process') or _('New')
        values['name'] = seq
        return super(RmaProcess, self).create(values)

    @api.onchange('client_id')
    def _onchange_clinet_id(self):

        domain = {}
        gps_device_ids = []
        accessory_ids = []

        values = self.env['lgps.device'].search([('client_id', "=", self.client_id.id)])
        for value in values:
            gps_device_ids.append(value.id)

        values = self.env['lgps.accessory'].search([('client_id', "=", self.client_id.id)])
        for value in values:
            accessory_ids.append(value.id)

        domain = {
            'gps_device_ids': [('id', 'in', gps_device_ids)],
            'accessories_id': [('id', 'in', accessory_ids)],
        }

        return {'domain': domain}

    @api.onchange('apply_to')
    def _onchange_apply_to(self):
        if self.apply_to == 'gps_devices':
            self.accessories_id = False
        if self.apply_to == 'accessories':
            self.device_id = False

    def action_shipment_to_supplier(self):
        self.write({'state': 'shipment_to_supplier'})
        return True

    def action_delivery_to_customer(self):
        self.write({'state': 'delivery_to_customer'})
        return True

    def action_done(self):
        self.write({'state': 'done'})

        problem = self.problem if self.problem else 'NA'
        diagnostic = self.diagnostic if self.diagnostic else 'NA'
        track_number = self.track_number if self.track_number else 'NA'
        observations = self.observations if self.observations else 'NA'
        shipped_date = self.shipped_date.strftime('%Y-%m-%d') if self.shipped_date else 'NA'
        return_date = self.return_date.strftime('%Y-%m-%d') if self.return_date else 'NA'

        body = '<br/><b>Proceso de: </b> ' + self.name + '<br/>'
        body += '<br/><b>Fecha:</b> ' + self.create_date.strftime('%Y-%m-%d')
        body += '<br/><b>Entrega:</b> ' + self.assigned_to.name
        body += '<br/><b>Falla:</b> ' + problem
        body += '<br/><b>Diagnóstico:</b> ' + diagnostic
        body += '<br/><b>Fecha Envío:</b> ' + shipped_date
        body += '<br/><b>No. Guía:</b> ' + track_number
        body += '<br/><b>Fecha de Regreso:</b> ' + return_date
        body += '<br/><b>Observaciones:</b> ' + observations

        if self.device_id:
            self.device_id.message_post(body=body)
        else:
            if self.accessories_id:
                self.accessories_id.message_post(body=body)

        self.sendNotificationEmail(body)
        return True

    def sendNotificationEmail(self, body):

        template = self.env.ref('lgps_rma.rma_finished_email_template')
        res = self.env['mail.template'].browse(template.id).send_mail(self.id)

    # def action_send_email(self):
    #     self.ensure_one()
    #     ir_model_data = self.env['ir.model.data']
    #     try:
    #         template_id =    ir_model_data._xmlid_lookup('lgps_rma.rma_finished_email_template')[2]
    #     except ValueError:
    #         template_id = False
    #
    #     try:
    #         compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[2]
    #     except ValueError:
    #         compose_form_id = False
    #         template_id = self.env.ref('event.event_registration_mail_template_badge')
    #         compose_form = self.env.ref('mail.email_compose_message_wizard_form')
    #
    #         ctx = {
    #             'default_model': "example.email",
    #             'default_res_id': self.ids[0],
    #             'default_use_template': bool(template_id),
    #             'default_template_id': template_id,
    #             'default_composition_mode': 'comment',
    #             'mark_so_as_sent': True,
    #             'force_email': True
    #         }
    #
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'view_type': 'form',
    #             'view_mode': 'form',
    #             'res_model': 'mail.compose.message',
    #             'views': [(compose_form.id, 'form')],
    #             'view_id': compose_form.id,
    #             'target': 'new',
    #             'context': ctx,
    #         }
