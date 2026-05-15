# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class CommonOperationsToAccessoriesWizard(models.TransientModel):
    _name = "lgps.accessory_operations"
    _description = _("Common Operations Wizard For Accessories")

    def _default_accessories(self):
        return self.env['lgps.accessory'].browse(self._context.get('active_ids'))

    operation_mode = fields.Selection(
        [
            ('replacement', _('Warranty Replacement')),
            ('substitution', _('Subsitution by new')),
        ],
        default="replacement"
    )

    accessories_ids = fields.Many2many(
        comodel_name='lgps.accessory',
        string=_("Accessory"),
        required=True,
        default=_default_accessories,
    )

    destination_accessories_ids = fields.Many2one(
        comodel_name='lgps.accessory',
        string=_("Substitute accessory"),
        domain="[('id', 'in', allowed_accessories_ids)]",
    )

    related_odt = fields.Many2one(
        comodel_name='repair.order',
        string=_("Work order related"),
    )

    requested_by = fields.Char(
        string=_("Requested by"),
    )

    comment = fields.Text(
        string=_("Operation Reason"),
        required=True,
    )

    related_field_service = fields.Many2one(
        comodel_name="project.task",
        string=_("Related work order"),
        domain="[('id', 'in', allowed_field_services_ids)]",
    )

    allowed_field_services_ids = fields.Many2many(
        comodel_name="project.task",
        compute="_compute_allowed_value_ids"
    )

    allowed_accessories_ids = fields.Many2many(
        comodel_name="lgps.accessory",
        compute="_compute_allowed_accessories_ids"
    )

    @api.depends("related_field_service")
    def _compute_allowed_value_ids(self):
        active_model = self._context.get('active_model')
        active_records = self.env[active_model].browse(self._context.get('active_ids'))

        if not active_model:
            raise UserError('No active model detected')

        include = []
        for r in active_records:
            include.append(r.client_id.id)

        for record in self:
            record.allowed_field_services_ids = self.env["project.task"].search([
                ['partner_id', 'in', include]
            ])

    @api.depends("destination_accessories_ids")
    def _compute_allowed_accessories_ids(self):
        active_model = self._context.get('active_model')
        active_records = self.env[active_model].browse(self._context.get('active_ids'))

        exclude = []
        for accessory in active_records:
            exclude.append(accessory.id)

        for record in self:
            log = self.env["lgps.accessory"].search([
                ['id', 'not in', exclude],
                ['status', 'in', [
                    'inventory', 'demo', 'comodato', 'borrowed', 'replacement', 'foreign_inventory', 'replacement'
                ]],
            ])

            record.allowed_accessories_ids = log
            return log

    def execute_operation(self):
        if len(self._context.get('active_ids')) < 1:
            raise UserError(_('Select at least one record.'))

        # Replacement
        if self.operation_mode == 'replacement':
            self.execute_replacement()
        # Substitution
        # if self.operation_mode == 'substitution':
        #     self.execute_substitution()

        return {}

    def execute_replacement(self):
        lgps_config = self.sudo().env['ir.config_parameter']
        channel_id = lgps_config.get_param('lgps.device_wizard.substitution_default_channel')

        if not channel_id:
            raise UserError(_(
                'There is not configuration for default channel.\n Configure this in order to send the notification.'))

        self._check_mandatory_fields(['comment', 'related_field_service'])

        # Obtenemos los Ids seleccionados
        active_model = self._context.get('active_model')
        active_records = self.env[active_model].browse(self._context.get('active_ids'))
        assigned_to = lgps_config.get_param('lgps.device_wizard.repairs_default_user')

        body_title = "<b class='text-info'>[Proceso de Sustitución por Garantía]</b><br/><br/>"
        repair_internal_notes = body_title
        repair_internal_notes += 'El accesorio REEMPLAZADO / REEMPLAZADO_SERIE se reemplazó con el accesorio: EQUIPO ' \
                                '/ EQUIPO_SERIE en el dispositivo DEVICE '
        repair_internal_notes += 'durante la atención del servicio: RELATED_ODT.'

        operation_log_comment = body_title
        operation_log_comment += 'El accesorio REEMPLAZADO / REEMPLAZADO_SERIE se reemplaza con el accesorio '
        operation_log_comment += 'EQUIPO / EQUIPO_SERIE en el equipo DEVICE '
        operation_log_comment += 'durante la atención del servicio RELATED_ODT debido a que está dentro de garantía. <br/><br/>'
        # operation_log_comment += 'El accesorio pasa a propiedad de la empresa.<br/><br/>'
        operation_log_comment += 'Se entrega accesorio a soporte para revisión con número de  reparación RMA_ODT.'
        operation_log_comment += '<br/><br/>Comentario: ' + self.comment

        operation_log_comment_accessory = body_title
        operation_log_comment_accessory += 'Se coloca accesorio como reemplazo para el accesorio EQUIPO / EQUIPO_SERIE '
        operation_log_comment_accessory += 'en el equipo DEVICE con la ODT RELATED_ODT mientras está en revisión '
        operation_log_comment_accessory += 'con número de  reparación RMA_ODT por estar dentro de garantía.<br/><br/>'
        operation_log_comment_accessory += 'Comentario: ' + self.comment

        device_operation_log_comment = 'El accesorio REEMPLAZADO / REEMPLAZADO_SERIE se reemplazó con el accesorio: '
        device_operation_log_comment += ' EQUIPO / EQUIPO_SERIE debido a que esta dentro de garantía. <br/><br/>'
        device_operation_log_comment += 'Comentario: ' + self.comment

        replacement_accessory_comment = body_title
        replacement_accessory_comment += 'Este accesorio ha reemplazado al accesorio REEMPLAZADO / REEMPLAZADO_SERIE '
        replacement_accessory_comment += 'durante la atención del servicio RELATED_ODT que está dentro de garantía.'
        replacement_accessory_comment += '<br/><br/>'
        replacement_accessory_comment += 'Se realiza la asociación correspondiente con el dispositivo DEVICE.'

        for accessory in active_records:

            if not accessory.device_id:
                raise UserError(
                    _('The selected accessory does not have any gps devices associated.\nCannot process any further.')
                )

            # Preparando Datos para la suscripcion
            serial_number_id = accessory.serial_number_id
            gps_device = accessory.device_id
            replaced_accesory_link = accessory._get_html_link()
            new_accessory_link = self.destination_accessories_ids._get_html_link()
            fsm_service_link = self.related_field_service._get_html_link()
            gps_device_link = gps_device._get_html_link()
            nodt = self.create_repair_record(accessory, assigned_to)
            nodt_link = nodt._get_html_link()

            if not gps_device:
                raise UserError(
                    _('The selected accessory does not have any gps devices associated.\nCannot process any further.')
                )
            if not accessory.warranty_start_date:
                raise UserError(_('There is not warranty date information.\n The task cannot be cmplpeted.'))

            operation_log_comment_accessory += '<br/><br/>Fecha de garantía de: ' + accessory.warranty_start_date.strftime('%Y-%m-%d')
            operation_log_comment_accessory += ' a ' + accessory.warranty_end_date.strftime('%Y-%m-%d')

            repair_internal_notes = repair_internal_notes.replace("REEMPLAZADO_SERIE", serial_number_id.name or 'NA')
            repair_internal_notes = repair_internal_notes.replace("REEMPLAZADO", replaced_accesory_link)
            repair_internal_notes = repair_internal_notes.replace("EQUIPO_SERIE", self.destination_accessories_ids.serial_number_id.name or 'NA')
            repair_internal_notes = repair_internal_notes.replace("EQUIPO", new_accessory_link)
            repair_internal_notes = repair_internal_notes.replace("RELATED_ODT", fsm_service_link)
            repair_internal_notes = repair_internal_notes.replace("DEVICE", gps_device_link)
            repair_internal_notes = repair_internal_notes.replace("NICK", gps_device.nick or '~')

            device_operation_log_comment = device_operation_log_comment.replace("REEMPLAZADO_SERIE", serial_number_id.name or 'NA')
            device_operation_log_comment = device_operation_log_comment.replace("REEMPLAZADO", replaced_accesory_link)
            device_operation_log_comment = device_operation_log_comment.replace("EQUIPO_SERIE", self.destination_accessories_ids.serial_number_id.name or 'NA')
            device_operation_log_comment = device_operation_log_comment.replace("EQUIPO", new_accessory_link)

            operation_log_comment = operation_log_comment.replace("REEMPLAZADO_SERIE", serial_number_id.name or 'NA')
            operation_log_comment = operation_log_comment.replace("REEMPLAZADO", replaced_accesory_link)
            operation_log_comment = operation_log_comment.replace('EQUIPO_SERIE', self.destination_accessories_ids.serial_number_id.name or 'NA')
            operation_log_comment = operation_log_comment.replace('EQUIPO', new_accessory_link)
            operation_log_comment = operation_log_comment.replace('RELATED_ODT', fsm_service_link)
            operation_log_comment = operation_log_comment.replace("DEVICE", gps_device_link)
            operation_log_comment = operation_log_comment.replace("NICK", gps_device.nick or '~')
            operation_log_comment = operation_log_comment.replace("RMA_ODT", nodt_link)

            operation_log_comment_accessory = operation_log_comment_accessory.replace('EQUIPO_SERIE', serial_number_id.name or 'NA')
            operation_log_comment_accessory = operation_log_comment_accessory.replace('EQUIPO', replaced_accesory_link)
            operation_log_comment_accessory = operation_log_comment_accessory.replace('RELATED_ODT', fsm_service_link)
            operation_log_comment_accessory = operation_log_comment_accessory.replace("DEVICE", gps_device_link)
            operation_log_comment_accessory = operation_log_comment_accessory.replace("NICK", gps_device.nick or '~')
            operation_log_comment_accessory = operation_log_comment.replace("RMA_ODT", nodt_link)

            replacement_accessory_comment = replacement_accessory_comment.replace("REEMPLAZADO_SERIE", serial_number_id.name or 'NA')
            replacement_accessory_comment = replacement_accessory_comment.replace("REEMPLAZADO", replaced_accesory_link)
            replacement_accessory_comment=replacement_accessory_comment.replace("DEVICE", gps_device_link)
            replacement_accessory_comment=replacement_accessory_comment.replace('RELATED_ODT', fsm_service_link)

            self.create_device_log(gps_device, accessory, device_operation_log_comment)
            self._complete_relations(gps_device, self.destination_accessories_ids)

            self.destination_accessories_ids.write({
                'status': 'replacement',
                'client_id': gps_device.client_id.id,
                # 'installation_date': accessory.installation_date
                'warranty_start_date': accessory.warranty_start_date
            })

            # Estatus del Equipo como desinstalado
            accessory.write({
                'status': "uninstalled",
                # "client_id": self.env.user.company_id.id,
                'device_id': False,

            })
            accessory.message_post(body=operation_log_comment, body_is_html=True)
            gps_device.message_post(body=device_operation_log_comment, body_is_html=True)

            self.create_accesory_log(accessory, operation_log_comment, nodt)
            self.log_to_channel(channel_id, operation_log_comment)
            self.destination_accessories_ids.message_post(body=replacement_accessory_comment, body_is_html=True)

        return {}

    def execute_substitution(self):
        # Check mandatory fields
        self._check_mandatory_fields(['comment', 'related_odt'])

        lgps_config = self.sudo().env['ir.config_parameter']
        channel_id = lgps_config.get_param('lgps.device_wizard.substitution_default_channel')
        default_list_price = lgps_config.get_param('lgps.device_wizard.repairs_default_price_list_id')

        if not channel_id:
            raise UserError(_(
                'There is not configuration for default channel.\n '
                'Configure this in order to send the notification.'
            ))

        if not default_list_price:
            raise UserError(_(
                'There is not configuration for default list price in RMA repairs.\n Configure this option first.'))

        # Messages to Log on Models
        operation_log_comment = 'Se desinstala el accesorio <strong>SUSTITUIDO / SUSTITUIDO_SERIE</strong> del '
        operation_log_comment += 'dispositivo DEVICE - NICK en la ODT RELATED_ODT '
        operation_log_comment += 'y se instala como nuevo el <strong>SUSTITUYE / SUSTITUYE_SERIE</strong>  el día FECHA_INSTALACION<br>'
        #operation_log_comment += 'Inicia garantía el FECHA_INSTALACION<br><br>'
        operation_log_comment += 'Comentario: ' + self.comment

        # Log to New Device
        operation_log_comment_device = 'Se instala como nuevo el accesorio <strong>SUSTITUYE / SUSTITUYE_SERIE</strong> '
        operation_log_comment_device += 'en el dispositivo DEVICE - NICK en la ODT RELATED_ODT y se desinstala el  <strong>SUSTITUIDO / SUSTITUIDO_SERIE</strong> '
        operation_log_comment_device += 'el día FECHA_INSTALACION_NUEVO<br><br>'
        operation_log_comment_device += 'Garantía: INICIO_GARANTIA a FIN_GARANTIA'

        # Obtenemos los Ids seleccionados
        active_model = self._context.get('active_model')
        active_records = self.env[active_model].browse(self._context.get('active_ids'))

        for accessory in active_records:

            # Preparando Datos para la ODT
            serial_number_id = accessory.serial_number_id
            client_id = accessory.client_id
            gps_device = accessory.device_id

            if not gps_device:
                raise UserError(_(
                    'The selected accessory does not have any gps devices associated.\nCannot process any further.'))

            # 1) Quitar del dispositivo GPS el accesorio desinstalado
            # 3) Cambiar el estatus del viejo a "desinstalado"

            # Comments to log on the operation log comment
            instalation_date = ''
            if self.destination_accessories_ids.installation_date:
                instalation_date = self.destination_accessories_ids.installation_date.strftime('%Y-%m-%d')

            operation_log_comment = operation_log_comment.replace("SUSTITUIDO_SERIE", serial_number_id.name or 'NA')
            operation_log_comment = operation_log_comment.replace("SUSTITUIDO", accessory.name)
            operation_log_comment = operation_log_comment.replace('DEVICE', gps_device.name)
            operation_log_comment = operation_log_comment.replace('NICK', gps_device.nick or '~')
            operation_log_comment = operation_log_comment.replace('RELATED_ODT', self.related_odt.name)
            operation_log_comment = operation_log_comment.replace('SUSTITUYE_SERIE', self.destination_accessories_ids.serial_number_id.name or 'NA')
            operation_log_comment = operation_log_comment.replace('SUSTITUYE', self.destination_accessories_ids.name)
            operation_log_comment = operation_log_comment.replace("FECHA_INSTALACION", instalation_date)

            # Estatus del Equipo como desinstalado
            self.create_device_log(gps_device, accessory, operation_log_comment)
            self._complete_relations(gps_device, self.destination_accessories_ids)

            accessory.write({
                'device_id': None,
                'status': "drop"
            })

            accessory.message_post(body=operation_log_comment)

            # 2) Colocar el cliente en el nuevo accesorio, en el anterior dejar el mismo
            # 4) La fecha de instalación del nuevo será la real nueva (la pondrá monitoreo en las pruebas) y fecha de
            # inicio de garantía será la misma que la fecha de instalación, la fecha fin será 12 meses después.
            # 5)Agregar el comentario a ambos:

            start_date = ''
            if self.destination_accessories_ids.warranty_start_date:
                start_date = self.destination_accessories_ids.warranty_start_date.strftime('%Y-%m-%d')

            end_date = ''
            if self.destination_accessories_ids.warranty_end_date:
                end_date = self.destination_accessories_ids.warranty_end_date.strftime('%Y-%m-%d')

            operation_log_comment_device = operation_log_comment_device.replace("SUSTITUIDO_SERIE", serial_number_id.name or 'NA')
            operation_log_comment_device = operation_log_comment_device.replace("SUSTITUIDO", accessory.name)
            operation_log_comment_device = operation_log_comment_device.replace('RELATED_ODT', self.related_odt.name)
            operation_log_comment_device = operation_log_comment_device.replace('SUSTITUYE_SERIE', self.destination_accessories_ids.serial_number_id.name or 'NA')
            operation_log_comment_device = operation_log_comment_device.replace('SUSTITUYE', self.destination_accessories_ids.name)
            operation_log_comment_device = operation_log_comment_device.replace('DEVICE', gps_device.name)
            operation_log_comment_device = operation_log_comment_device.replace('NICK', gps_device.nick or '~')
            operation_log_comment_device = operation_log_comment_device.replace("FECHA_INSTALACION_NUEVO", instalation_date)
            operation_log_comment_device = operation_log_comment_device.replace("INICIO_GARANTIA", start_date)
            operation_log_comment_device = operation_log_comment_device.replace("FIN_GARANTIA", end_date)

            self.destination_accessories_ids.write({
                'status': 'installed',
                'client_id': gps_device.client_id.id,
                'warranty_start_date': self.destination_accessories_ids.installation_date,
                'warranty_term': '12',
            })

            self.destination_accessories_ids.message_post(body=operation_log_comment_device)
            self.create_accesory_log(accessory, operation_log_comment)
            self.log_to_channel(channel_id, operation_log_comment)

        return {}

    def return_active_records(self):
        active_model = self._context.get('active_model')
        active_records = self.env[active_model].browse(self._context.get('active_ids'))

        return active_records

    def chek_status_before_further_process(self, accessories, status):
        error = False
        buffer = ''

        for accessory in accessories:
            if accessory.status != status or accessory.platform == 'Drop':
                error = True
                buffer += accessory.name + '  /  ' + accessory.status + '  /  ' + accessory.serial_number_id.name + '\n'

        if error:
            raise UserError(
                _('Some accessories does not has the right status for this operation.\n\n ' + buffer)
            )

        return {}

    def get_price_from_pricelist(self, price_list, product):
        lista_de_precios = self.sudo().env['product.pricelist'].search([('id', '=', price_list)], limit=1)
        if lista_de_precios:
            precio_de_lista = lista_de_precios.get_product_price(product, 1, False)
            if precio_de_lista:
                price = precio_de_lista
            else:
                price = 0
        else:
            price = product.lst_price

        return price

    def create_odt(self, dictionary):
        odt_object = self.env['repair.order']
        odt = odt_object.create(dictionary)
        return odt

    def _check_mandatory_fields(self, rules):
        for rule in rules:

            if not getattr(self, rule):
                raise UserError(self._get_error_message_for_field(rule))

    def _get_error_message_for_field(self, field=''):
        if field == 'comment':
            return _('You forgot to comment the reason for this process to run.')
        if field == 'requested_by':
            return _('Who authorizes this request?')
        if field == 'related_odt':
            return _('You forgot to select the Related ODT')
        return

    def create_device_log(self, device, accessory, log_comment="",  nodt=None):
        log_object = self.env['lgps.device_history']
        repar_id = nodt.id if nodt else None

        dictionary = {
            'name': device.name + ' - ' + self.operation_mode,
            'product_id': device.product_id.id,
            'serial_number_id': device.serial_number_id.id,
            'client_id': device.client_id.id,
            'device_ids': device.id,
            'destination_device_ids': False,
            'operation_mode': 'acc_replacement',
            'related_odt': repar_id,
            'related_service': self.related_field_service.id,
            'requested_by': self.requested_by,
            'comment': self.comment,
            'log_msn': log_comment
        }
        device_log = log_object.create(dictionary)
        return device_log

    def create_accesory_log(self, accessory, log_comment="", nodt=False):
        log_object = self.env['lgps.accessory_history']

        dictionary = {
            'name': accessory.name + ' - ' + self.operation_mode,
            'product_id': accessory.product_id.id,
            'serial_number_id': accessory.serial_number_id.id,
            'client_id': accessory.client_id.id,
            'accessory_ids': accessory.id,
            'destination_accessory_ids': self.destination_accessories_ids.id,
            'operation_mode': self.operation_mode,
            'related_odt': nodt.id,
            'related_service': self.related_field_service.id,
            'requested_by': self.requested_by,
            'comment': self.comment,
            'log_msn': log_comment
        }
        device_log = log_object.create(dictionary)
        return device_log

    def log_to_channel(self, channel_id, channel_msn):

        if not channel_id:
            raise UserError(
                _('There is not configuration for default channel.\n Configure this in order to send the notification.')
            )
        else:
            channel_notifier = self.sudo().env['discuss.channel'].search([('id', '=', channel_id)])
            channel_notifier.with_user(self.env.user).message_post(
                body=channel_msn,
                subtype_xmlid='mail.mt_note',
                message_type='comment',
                body_is_html=True
            )

        return {}

    def _complete_relations(self, device, accessory):
        accessory.write({
            'device_id': device.id
        })

        device.accessory_ids = [(4, accessory.id, 0)]
        return

    @api.onchange('destination_accessories_ids')
    def _onchange_destination_accessories_ids(self):
        domain = {}
        destination_accessories_ids = []

        if not self.destination_accessories_ids:
            active_model = self._context.get('active_model')
            active_records = self.env[active_model].browse(self._context.get('active_ids'))
            for record in active_records:
                accessories_obj = self.env['lgps.accessory'].search([('device_id', '=', record.device_id.id)])
                accessories_results = accessories_obj - active_records
                for accessory in accessories_results:
                    destination_accessories_ids.append(accessory.id)

            # to assign parter_list value in domain
            domain = {'destination_accessories_ids': [('id', 'in', destination_accessories_ids)]}

        return {'domain': domain}

    def create_repair_record(self, device, assigned_to):
        repair_name = self.env['ir.sequence'].sudo().next_by_code('repair.order')
        repair_object = self.env['repair.order']
        dictionary = {
            'name': repair_name,
            'state': 'draft',
            'partner_id': device.client_id.id,
            'product_id': device.product_id.id,
            'lot_id': device.serial_number_id.id,
            'user_id': assigned_to,
        }

        repair = repair_object.create(dictionary)
        return repair
