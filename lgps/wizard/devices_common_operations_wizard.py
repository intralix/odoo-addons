# -*- coding: utf-8 -*-
import json
import time
from datetime import timedelta
from odoo import api, models, fields, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class CommonDevicesOperationsWizard(models.TransientModel):
    _name = "lgps.device_operations"
    _description = _("Common Operations Wizard For Devices")

    @api.model
    def _default_stage_id(self):
        stage = self.env["lgps.device_stage"]
        return stage.search([
            ("state", "=", "ready_to_install")
        ], limit=1)

    def _default_devices(self):
        return self.env['lgps.device'].browse(self._context.get('active_ids'))

    operation_mode = fields.Selection(
        [
            ('add_reactivate', _('Alta / Reactivación de equipo')),
            ('drop', _('Baja de equipos')),
            ('wakeup', _('Deshibernación de equipos')),
            ('hibernation', _('Hibernación de equipos')),
            ('loan_substitution', _('Reemplazo de comodato')),
            ('replacement', _('Reemplazo de equipo por garantía')),
            ('substitution', _('Sustitución de equipo por revisión'))
        ],
        default='drop'
    )

    reason = fields.Selection(
        [
            ('bad_service', _('Mal Servicio')),
            ('vehicle_sold', _('Venta de Unidad')),
            ('wrecked_vehicle', _('Unidad siniestrada')),
            ('client_warehouse', _('Sin uso, en resguardo con el cliente')),
            ('own_warehouse', _('Error administrativo')),
            ('non_repairable', _('Equipo gps no reparable')),
            ('financial_situation', _('Cancelación de cuenta por falta de pago')),
            ('change_of_supplier', _('Cambio de proveedor por precio')),
            ('return_to_stock', _('Regresa a Almacén Respaldo/Provisional/Prestado')),
            ('return_from_loan', _('Regresa a Almacén Estuvo en Comodato')),
            ('on_stock_not_assigned', _('En almacén Intralix sin asignación')),
            ('replacement', _('Por reemplazo de Equipo')),
            ('platform_change', _('Cambio de plataforma Intralix')),
            ('financial_debts', _('Baja por falta de pago')),
        ],
    )

    device_ids = fields.Many2many(
        comodel_name='lgps.device',
        string="Gps Device",
        required=True,
        default=_default_devices,
    )

    destination_device_ids = fields.Many2one(
        comodel_name='lgps.device',
        string=_("Substitute equipment"),
        domain="[('id', 'in', allowed_devices_ids)]",
    )

    related_odt = fields.Many2one(
        comodel_name='repair.order',
        string=_("Work order related"),
    )

    related_field_service = fields.Many2one(
        comodel_name="project.task",
        string=_("Related work order"),
        domain="[('id', 'in', allowed_field_services_ids)]",
    )

    requested_by = fields.Char(
        string=_("Requested by"),
    )

    comment = fields.Text(
        string=_("Operation Reason"),
        required=True,
    )

    devices_list = fields.Text(
        string=_("Devices List")
    )

    cellchips_list = fields.Text(
        string=_("Cellchips List")
    )

    allowed_field_services_ids = fields.Many2many(
        comodel_name="project.task",
        compute="_compute_allowed_value_ids"
    )

    allowed_devices_ids = fields.Many2many(
        comodel_name="lgps.device",
        compute="_compute_allowed_device_ids"
    )

    @api.depends("related_field_service")
    def _compute_allowed_value_ids(self):
        active_model = self._context.get('active_model')
        active_records = self.env[active_model].browse(self._context.get('active_ids'))

        if not active_model:
            raise UserError('No active model detected')

        include = []
        for device in active_records:
            include.append(device.id)

        for record in self:
            record.allowed_field_services_ids = self.env["project.task"].search([['device_id', 'in', include]])

    @api.depends("destination_device_ids")
    def _compute_allowed_device_ids(self):
        active_model = self._context.get('active_model')
        active_records = self.env[active_model].browse(self._context.get('active_ids'))
        stage_ready_to_install = self.env.ref('lgps.stage_ready_to_install')
        _logger.warning('stage_ready_to_install: %s', stage_ready_to_install)
        _logger.warning('active_records: %s', active_records)
        exclude = []
        for device in active_records:
            exclude.append(device.id)

        for record in self:
            log = self.env["lgps.device"].search([
                ['id', 'not in', exclude],
                ['administrative_status', 'in', ['inventory', 'demo', 'comodato', 'borrowed', 'replacement']],
                ['stage_id', 'in', [stage_ready_to_install.id]],
            ])
            _logger.warning('log: %s', log)
            record.allowed_devices_ids = log
            _logger.warning('record.allowed_devices_ids: %s', record.allowed_devices_ids)
            return log

    # Available services
    tracking = fields.Boolean(default=False, string=_("Tracking"))
    fuel = fields.Boolean(default=False, string=_("Fuel"))
    fuel_hall = fields.Boolean(default=False, string=_("Efecto Hall"))
    scanner = fields.Boolean(default=False, string="Scanner")
    temperature = fields.Boolean(default=False, string=_("Temperature"))
    logistic = fields.Boolean(default=False, string=_("Logistic"))
    collective = fields.Boolean(default=False, string=_("Collective"))
    fleetrun = fields.Boolean(default=False, string=_("Fleetrun"))
    electronics = fields.Boolean(default=False, string=_("Electronics"))

    device_status = fields.Selection(
        selection=[
            ("drop", _("Drop")),
            ("comodato", _("Comodato")),
            ("courtesy", _("Courtesy")),
            ("demo", _("Demo")),
            ("uninstalled", _("Uninstalled")),
            ("external", _("External")),
            ("hibernate", _("Hibernate")),
            ("installed", _("Installed")),
            ("inventory", _("Inventory")),
            ("new", _("New")),
            ("for installing", _("For Installing")),
            ("borrowed", _("Borrowed")),
            ("tests", _("Tests")),
            ("replacement", _("Replacement")),
            ("backup", _("Backup")),
            ("rma", _("RMA")),
            ("sold", _("Sold")),
        ],
        default="inventory",
        string=_("Status"),
    )

    platform = fields.Selection(
        selection=[
            ("Ceiba2", "Ceiba2"),
            ("Cybermapa", "Cybermapa"),
            ("Drop", _("Drop")),
            ("Gurtam", "Gurtam"),
            ("Gurtam_Utrax", "Gurtam/Utrax"),
            ("Lkgps", "Lkgps"),
            ("Mapaloc", "Mapaloc"),
            ("Novit", "Novit"),
            ("Position Logic", "Position Logic"),
            ("Sosgps", "Sosgps"),
            ("Utrax", "Utrax"),
        ],
        string=_("Platform"),
    )

    platform_list_id = fields.Many2one(
        comodel_name="lgps.platform_list",
        string=_("Platform List"),
        ondelete="set null",
        index=True,
        domain=[('active', '=', True)],
    )

    stage_id = fields.Many2one(
        "lgps.device_stage",
        default=_default_stage_id,
        group_expand="_group_expand_stage_id",
    )

    cell_chip_id = fields.Many2one(
        comodel_name="lgps.cellchip",
        string=_("Cellchip Number"),
    )

    reactivation_reason = fields.Selection(
        [
            ('op1', _('Alta de equipo para pedido de venta')),
            ('op2', _('Alta de equipo para pruebas')),
            ('op3', _('Equipo como respaldo')),
            ('op4', _('Equipo como préstamo')),
            ('op5', _('Revisión de equipo')),
            ('op6', _('Solicitud de reactivación')),
        ],
        string=_("Motivo del Alta / Reactivación"),
        default="op1"
    )

    def execute_operation(self):
        if len(self._context.get('active_ids')) < 1:
            raise UserError(_('Select at least one record.'))

        # Determinamos el tipo de Operació a Realizar
        if self.operation_mode == 'drop':
            self.execute_deactivation()
        # Hibernation
        if self.operation_mode == 'hibernation':
            # raise UserError('El proceso de hibernación esta siendo revisado por lo que no esta disponible')
            self.execute_hibernation()
        # Replacement
        if self.operation_mode == 'replacement':
            # raise UserError('El proceso de reemplazo esta siendo revisado por lo que no esta disponible')
            self.execute_replacement()
        # Substitution
        if self.operation_mode == 'substitution':
            #raise UserError('El proceso de sustitución esta siendo revisado por lo que no esta disponible')
            self.execute_substitution()
        # Wakeup
        if self.operation_mode == 'wakeup':
            # raise UserError('El proceso de deshibernación esta siendo revisado por lo que no esta disponible')
            self.execute_wakeup()
        # # Reactivate
        if self.operation_mode == 'add_reactivate':
            # raise UserError('El proceso de reactivación esta siendo revisado por lo que no esta disponible')
            self.execute_add_reactivate()
        # # Loan Substitution
        if self.operation_mode == 'loan_substitution':
            # raise UserError('El proceso de reemplazo por sustitución esta siendo revisado por lo que no esta disponible')
            self.execute_loan_substitution()

        # self.publishMessageToQueue()
        return {}

    def execute_deactivation(self):
        # # We get the seleteced Ids

        active_model = self._context.get('active_model')
        active_records = self.env[active_model].browse(self._context.get('active_ids'))
        drop_platform = False
        drop_status = self.env.ref('lgps.stage_disconnected')

        # Buffer Vars
        cellchips_ids = []
        notify_cellchisp_list = ""
        notify_gps_list = ""
        requested_by = self.requested_by

        # # for each selected record, we are going to make some operations:
        for r in active_records:
            body = "<b class='text-danger'>[Proceso de Baja]</b><br/><br/>" + self.comment + '<br/>'
            acumulador = ""

            platform = r.platform_list_id.name if r.platform_list_id.name else 'Sin Plataforma'
            chip = r.cell_chip_id.name if r.cell_chip_id else 'Sin chip'
            pchip = r.cell_chip_id.provider if r.cell_chip_id else 'Sin chip'
            client = r.client_id.name if r.client_id else 'Sin Cliente'
            equipo = r.name
            nick = r.nick if r.nick else 'NA'
            reason = dict(self._fields['reason']._description_selection(self.env)).get(self.reason)

            acumulador += '<br/><b>Motivo:</b> ' + reason
            acumulador += '<br/><b>Plataforma:</b> ' + platform
            acumulador += '<br/><b>Cliente:</b> ' + client
            acumulador += '<br/><b>Solicitado Por:</b> ' + requested_by
            acumulador += '<br/><b>Equipo:</b> ' + equipo
            acumulador += '<br/><b>Nick:</b> ' + nick
            acumulador += '<br/><b>Línea:</b> ' + chip
            acumulador += '<br/><b>Prov. Linea:</b> ' + pchip

            if r.cell_chip_id:
                cellchips_ids.append(r.cell_chip_id.id)
                provider_chip_data = r.cell_chip_id.provider if r.cell_chip_id.provider else ''
                notify_cellchisp_list += '<br/>' + r.cell_chip_id.name + ' - ' + provider_chip_data

            notify_gps_list += '<br/>' + client + ' || ' + equipo + ' || ' + nick + ' || ' + platform

            # Comprobando funciones adicionales
            body += '<br/>' + acumulador
            body += self.inspect_device_functions(r)

            # Ejecutamos la Baja en el sistema
            values = {
                'tracking': False,
                'fuel': False,
                'fuel_hall': False,
                'scanner': False,
                'temperature': False,
                'logistic': False,
                'collective': False,
                'fleetrun': False,
                'administrative_status': 'drop',
                'platform_list_id': drop_platform,
                'stage_id': drop_status.id,
            }
            self.do_device_operation(r, body, drop_status, values)
            # Create Object Log
            self.create_device_log(r, body)

        self.cellchips_list = notify_cellchisp_list
        self.devices_list = notify_gps_list
        # We mark cell chips that need deactivation
        self.set_cellchips_to_deactivate(cellchips_ids)

        # We are going to look for the subscription and make some changes
        subscriptions = self.env['sale.order'].search([
            ['device_id', 'in', active_records.ids],
            ['is_subscription', '=', True],
            ['subscription_state', '=', '3_progress']
        ])
        # _logger.warning('subscriptions: %s', subscriptions)
        if subscriptions:
            self._change_subscriptions_stage(
                subscriptions,
                "<b class='text-danger'>[Proceso de Baja]</b><br/>El equipo se ha dado de baja en el sistema."
            )

        # Log for tracking process
        channel_msn = '<br/>Los equipos listados a continuación se procesaron para dar de baja por motivo de:<br/>'
        channel_msn += self.comment + '<br/>'
        channel_msn += self.devices_list
        channel_msn += '<br/><br/>Favor de ejecutar la baja la siguientes líneas:<br/>'
        channel_msn += self.cellchips_list

        # Log to Channel
        lgps_config = self.sudo().env['ir.config_parameter']
        channel_id = lgps_config.get_param('lgps.deactivation_device.default_channel')
        self.log_to_channel(channel_id, channel_msn)

        return {}

    def execute_hibernation(self):
        # We get selected Ids that we'll process for hibernation
        active_model = self._context.get('active_model')
        active_records = self.env[active_model].browse(self._context.get('active_ids'))

        # Get global configuration object to retrieve options from settings
        lgps_config = self.sudo().env['ir.config_parameter']

        # # We get all configuration parameters
        channel_id = lgps_config.get_param('lgps.hibernate_device_wizard.default_channel')
        subscription_close_stage = lgps_config.get_param('lgps.close_subscription.default_state')
        subscription_pause_stage = lgps_config.get_param('lgps.hibernate_subscription.default_state')
        # Device Hibernation Status
        hibernated_status = self.env.ref('lgps.stage_hibernated')

        # Buffer Vars
        notify_gps_list = ""

        # Procesamos los quipos seleccionados:
        for r in active_records:
            body = "<b class='text-warning'>[Proceso de Hibernación]</b><br/><br/>"
            body += "<b>Comentario:</b> " + self.comment + "<br/>"
            body += '<b>Solicitado por</b>: ' + self.requested_by + "<br/>"
            acumulador = "<b>Datos del Equipo</b><hr/>"

            platform = r.platform_list_id.name if r.platform_list_id.name else 'Sin Plataforma'
            chip = r.cell_chip_id.name if r.cell_chip_id else 'Sin chip'
            client = r.client_id.name if r.client_id else 'Sin Cliente'
            equipo = r.name
            nick = r.nick if r.nick else 'NA'

            acumulador += '<b>Plataforma:</b> ' + platform + '<br/>'
            acumulador += '<b>Cliente:</b> ' + client + '<br/>'
            acumulador += '<b>Equipo:</b> ' + equipo + '<br/>'
            acumulador += '<b>Nick:</b> ' + nick + '<br/>'
            acumulador += '<b>Línea:</b> ' + chip + '<br/>'

            notify_gps_list += '<br/>' + client + ' || ' + equipo + ' || ' + nick + ' || ' + platform

            # Comprobando funciones adicionales
            body += '<br/>' + acumulador
            body += self.inspect_device_functions(r)

            # Desactivamos funciones e hibernamos
            self.do_device_operation(r, body, hibernated_status)
            # Create Device Operation Log Record
            self.create_device_log(r, body)

            # Ajustando las suscripciones
            subscriptions_to_churn = []
            subscriptions = self.env['sale.order'].search([
                ['device_id', '=', r.id],
                ['subscription_state', '=', '3_progress']
            ])

            if subscriptions:
                for subscription in subscriptions:
                    # _logger.warning('subscription: %s', subscription)
                    subscriptions_to_churn.append(subscription.id)
                    sale_subscription = subscription.copy({
                        'subscription_state': '4_paused' #subscription_pause_stage
                    })
                    # Debemos copiar la subscripción
#                    _logger.warning('subscription copy: %s', sale_subscription)
                    if sale_subscription:
                        sale_subscription.message_post(
                            body="<div class='alert alert-warning' role='alert'>"
                                 "<h4 class='alert-heading'>Atención!!!</h4>"
                                 "Esta subscripción de Hibernación se creo automáticamente<hr>"
                                 "Revise la información antes de ponerla en marcha.</div>",
                            body_is_html=True)
            else:
                raise UserError(_('El equipo ' + equipo + 'no tiene suscripción activa. No se puede Hibernar'))

        # Preparamos para notificar en los canales de comunicación el resultado del proceso
        self.devices_list = notify_gps_list
        # Obtenemos todas las suscripciones que debemos dar de baja
        subscriptions = self.env['sale.order'].search([['id', 'in', subscriptions_to_churn]])

        # Cerramos las suscripciones
        if subscriptions:
            self._change_subscriptions_stage(
                subscriptions,
                "<b class='text-warning'>[Proceso de Hibernación]</b><br/>El equipo se ha procesado como Hibernado en el sistema.",
                subscription_close_stage
            )

        #Log Channel
        channel_msn = '<br/>Los equipos mencionados a continuación se procesaron para ser hibernados por motivo de:<br/>'
        channel_msn += self.comment + '<br/> soliciato por: ' + self.requested_by + '<br/>'
        channel_msn += self.devices_list

        # Send Message
        self.log_to_channel(channel_id, channel_msn)
        return {}

    def execute_wakeup(self):
        # We get selected Ids that we'll process for hibernation
        active_model = self._context.get('active_model')
        active_records = self.env[active_model].browse(self._context.get('active_ids'))

        # Get global configuration object to retrieve options from settings
        lgps_config = self.sudo().env['ir.config_parameter']

        # # We get all configuration parameters
        channel_id = lgps_config.get_param('lgps.hibernate_device_wizard.default_channel')
        subscription_close_stage = lgps_config.get_param('lgps.close_subscription.default_state')
        subscription_pause_stage = lgps_config.get_param('lgps.hibernate_subscription.default_state')
        # Device Hibernation Status
        installed_status = self.env.ref('lgps.stage_installed')
        hibernated_status = self.env.ref('lgps.stage_hibernated')
        _logger.warning('hibernated_status: %s', hibernated_status)
        self.chek_status_before_further_process(active_records, hibernated_status)

        # Buffer Vars
        notify_gps_list = ""

        # Procesamos los quipos seleccionados:
        for r in active_records:
            body = "<b class='text-warning'>[Proceso de Des-hibernación]</b><br/><br/>"
            body += "<b>Comentario:</b> " + self.comment + "<br/>"
            body += '<b>Solicitado por</b>: ' + self.requested_by + "<br/>"
            acumulador = "<b>Datos del Equipo</b><hr/>"

            platform = r.platform_list_id.name if r.platform_list_id.name else 'Sin Plataforma'
            chip = r.cell_chip_id.name if r.cell_chip_id else 'Sin chip'
            client = r.client_id.name if r.client_id else 'Sin Cliente'
            equipo = r.name
            nick = r.nick if r.nick else 'NA'

            acumulador += '<b>Plataforma:</b> ' + platform + '<br/>'
            acumulador += '<b>Cliente:</b> ' + client + '<br/>'
            acumulador += '<b>Equipo:</b> ' + equipo + '<br/>'
            acumulador += '<b>Nick:</b> ' + nick + '<br/>'
            acumulador += '<b>Línea:</b> ' + chip + '<br/>'

            notify_gps_list += '<br/>' + client + ' || ' + equipo + ' || ' + nick + ' || ' + platform

            # Comprobando funciones adicionales
            body += '<br/>' + acumulador
            body += self.inspect_device_functions(r, True)

            values = {
                'fuel': self.fuel if self.fuel else r.fuel,
                'fuel_hall': self.fuel_hall if self.fuel_hall else r.fuel_hall,
                'scanner': self.scanner if self.scanner else r.scanner,
                'temperature': self.temperature if self.temperature else r.temperature,
                'logistic': self.logistic if self.logistic else r.logistic,
                'collective': self.collective if self.collective else r.collective,
                'tracking': self.tracking if self.tracking else r.tracking,
                'fleetrun': self.fleetrun if self.fleetrun else r.fleetrun,
                'stage_id': installed_status.id,
            }

            # Desactivamos funciones e hibernamos
            self.do_device_operation(r, body, hibernated_status, values)
            # Create Device Operation Log Record
            self.create_device_log(r, body)

            # Ajustando las suscripciones
            # Ajustando las suscripciones
            subscriptions_to_pause = []
            subscriptions = self.env['sale.order'].search([
                ['device_id', '=', r.id],
                ['subscription_state', '=', '3_progress']
            ])

            if subscriptions:
                for subscription in subscriptions:
                    subscriptions_to_pause.append(subscription.id)
                    subscription.message_post(
                        body="<div class='alert alert-warning' role='alert'>"
                             "<h4 class='alert-heading'>Atención!!!</h4>"
                             "Esta subscripción se debe modificar por que el equipo ha sido Des-Hibernado.<hr>"
                             "Revise que la información sea correcta antes de ponerla en marcha.</div>",
                        body_is_html=True)
            else:
                raise UserError(_('El equipo ' + equipo + 'no tiene suscripción activa. No se puede Hibernar'))

        # Preparamos para notificar en los canales de comunicación el resultado del proceso
        self.devices_list = notify_gps_list

        # Obtenemos todas las suscripciones que debemos pausar para ser modificadas
        subscriptions = self.env['sale.order'].search([['id', 'in', subscriptions_to_pause]])
        # Cerramos las suscripciones
        if subscriptions:
            self._change_subscriptions_stage(
                subscriptions,
                "<b class='text-warning'>[Proceso de Des-Hibernación]</b><br/>El equipo se ha procesado como Des-Hibernado en el sistema.",
                '4_paused'
            )

        # Log Channel
        channel_msn = '<br/>Los equipos mencionados a continuación se procesaron para ser des-hibernados por motivo de:<br/>'
        channel_msn += self.comment + '<br/> soliciato por: ' + self.requested_by + '<br/>'
        channel_msn += self.devices_list

        # Send Message
        self.log_to_channel(channel_id, channel_msn)
        return {}

    def execute_substitution(self):
        # We get selected Ids that we'll process for hibernation
        active_model = self._context.get('active_model')
        active_records = self.env[active_model].browse(self._context.get('active_ids'))

        # Get global configuration object to retrieve options from settings
        lgps_config = self.sudo().env['ir.config_parameter']

        # Check mandatory fields
        self._check_mandatory_fields(['comment', 'related_field_service'])

        channel_id = lgps_config.get_param('lgps.device_wizard.substitution_default_channel')
        if not channel_id:
            raise UserError(_(
                'There is not configuration for default channel.\n '
                'Configure this in order to send the notification.'
            ))

        replacement_status = self.env.ref('lgps.stage_installed')
        stage_rma_status = self.env.ref('lgps.stage_rma')

        body_title = "<b class='text-info'>[Proceso de Sustitución por Revisión]</b><br/><br/>"
        # Messages to Log on Models
        repair_internal_notes = body_title
        repair_internal_notes += 'El equipo SUSTITUIDO se sustituyó con el equipo: EQUIPO durante la atención'
        repair_internal_notes += ' del servicio: RELATED_ODT<br/>'

        operation_log_comment = body_title
        operation_log_comment += 'El equipo SUSTITUIDO se retira mientras que esta en revisión con número de reparación'
        operation_log_comment += ' RMA_ODT  <br/><br/> Se instala el equipo EQUIPO en su lugar durante la atención del'
        operation_log_comment += ' servicio RELATED_ODT <br/><br/>'
        operation_log_comment += 'Se entrega equipo al área de calidad para revisión.<br/><br/>'
        operation_log_comment += 'Comentario: ' + self.comment

        operation_log_comment_device = body_title
        operation_log_comment_device += 'Se instala el equipo SUSTITUIDO como sustituto de EQUIPO mientras está en '
        operation_log_comment_device += 'revisión con número de  reparación RMA_ODT <br/><br/>'
        operation_log_comment_device += 'Comentario: ' + self.comment

        for device in active_records:
            if not device.warranty_start_date:
                raise UserError(_(
                    'The device does not have Warranty Start Date. \n'
                    'Complete this first in order to process the Substitution Operation.'
                ))

            # We take original values from removed device
            client_id = device.client_id
            assigned_to = lgps_config.get_param('lgps.device_wizard.repairs_default_user')
            replaced_device_link = device._get_html_link()
            new_device_link = self.destination_device_ids._get_html_link()
            fsm_service_link = self.related_field_service._get_html_link()

            repair_internal_notes = repair_internal_notes.replace("SUSTITUIDO", replaced_device_link)
            repair_internal_notes = repair_internal_notes.replace("EQUIPO", new_device_link)
            repair_internal_notes = repair_internal_notes.replace("RELATED_ODT", fsm_service_link)

            nodt = self.create_repair_record(device, assigned_to)
            nodt_link = nodt._get_html_link()
            _logger.warning('nodt: %s', nodt)

            # We are goint to look for the removed device subscription to update to installed device
            subscription = self.env['sale.order'].search([
                ['device_id', '=', device.id],
                ['subscription_state', '=', '3_progress']
            ])

            if subscription:
                subscription.write({'device_id': self.destination_device_ids.id})
                _logger.warning('self.destination_device_ids.id: %s', self.destination_device_ids.id)
                subscription.message_post(body=repair_internal_notes, body_is_html=True)

            # Comments to log on the operation log comment
            repair_internal_notes = repair_internal_notes.replace("RMA_ODT", nodt_link)
            operation_log_comment = operation_log_comment.replace("RMA_ODT", nodt_link)
            operation_log_comment = operation_log_comment.replace("SUSTITUIDO", replaced_device_link)
            operation_log_comment = operation_log_comment.replace('EQUIPO', new_device_link)
            operation_log_comment = operation_log_comment.replace('RELATED_ODT', fsm_service_link)

            # We update replaced device data
            values = {
                'administrative_status': "rma",
                'stage_id': stage_rma_status.id
            }
            self.do_device_operation(device, operation_log_comment, stage_rma_status, values)

            operation_log_comment_device = operation_log_comment_device.replace('EQUIPO', replaced_device_link)
            operation_log_comment_device = operation_log_comment_device.replace('SUSTITUIDO', new_device_link)
            operation_log_comment_device = operation_log_comment_device.replace('RMA_ODT', nodt_link)

            values = {
                'administrative_status': "borrowed",
                'client_id': client_id.id,
                'stage_id': replacement_status.id,
            }
            self.do_device_operation(self.destination_device_ids, operation_log_comment_device, replacement_status, values)
            self.create_device_log(device, operation_log_comment, nodt)
            self.log_to_channel(channel_id, operation_log_comment)

        # Check mandatory fields
        return {}

    def execute_replacement(self):

        # We get selected Ids that we'll process for hibernation
        active_model = self._context.get('active_model')
        active_records = self.env[active_model].browse(self._context.get('active_ids'))

        # Get global configuration object to retrieve options from settings
        lgps_config = self.sudo().env['ir.config_parameter']

        # Check mandatory fields
        self._check_mandatory_fields(['comment', 'related_field_service'])

        channel_id = lgps_config.get_param('lgps.device_wizard.substitution_default_channel')
        if not channel_id:
            raise UserError(_(
                'There is not configuration for default channel.\n '
                'Configure this in order to send the notification.'
            ))

        replacement_status = self.env.ref('lgps.stage_installed')
        stage_rma_status = self.env.ref('lgps.stage_rma')

        body_title = "<b class='text-info'>[Proceso de Sustitución por Garantía]</b><br/><br/>"
        # Messages to Log on Models
        repair_internal_notes = body_title
        repair_internal_notes += 'El equipo SUSTITUIDO se sustituyó con el equipo: EQUIPO durante la atención'
        repair_internal_notes += ' del servicio: RELATED_ODT<br/>'

        operation_log_comment = body_title
        operation_log_comment += 'El equipo SUSTITUIDO se retira mientras que esta en revisión con número de reparación'
        operation_log_comment += ' RMA_ODT  <br/><br/> Se instala el equipo EQUIPO en su lugar durante la atención del'
        operation_log_comment += ' servicio RELATED_ODT <br/><br/>'
        operation_log_comment += 'Se entrega equipo al área de calidad para revisión.<br/><br/>'
        operation_log_comment += 'Comentario: ' + self.comment

        operation_log_comment_device = body_title
        operation_log_comment_device += 'Se instala el equipo SUSTITUIDO como sustituto de EQUIPO mientras está en '
        operation_log_comment_device += 'revisión con número de  reparación RMA_ODT <br/><br/>'
        operation_log_comment_device += 'Comentario: ' + self.comment

        for device in active_records:
            if not device.warranty_start_date:
                raise UserError(_(
                    'The device does not have Warranty Start Date. \n'
                    'Complete this first in order to process the Substitution Operation.'
                ))

            # We take original values from removed device
            client_id = device.client_id
            assigned_to = lgps_config.get_param('lgps.device_wizard.repairs_default_user')
            replaced_device_link = device._get_html_link()
            new_device_link =  self.destination_device_ids._get_html_link()
            fsm_service_link = self.related_field_service._get_html_link()

            repair_internal_notes = repair_internal_notes.replace("SUSTITUIDO", replaced_device_link)
            repair_internal_notes = repair_internal_notes.replace("EQUIPO", new_device_link)
            repair_internal_notes = repair_internal_notes.replace("RELATED_ODT", fsm_service_link)

            nodt = self.create_repair_record(device, assigned_to)
            nodt_link = nodt._get_html_link()
            _logger.warning('nodt: %s', nodt)

            # We are goint to look for the removed device subscription to update to installed device
            subscription = self.env['sale.order'].search([
                ['device_id', '=', device.id],
                ['subscription_state', '=', '3_progress']
            ])

            if subscription:
                subscription.write({
                    'device_id': self.destination_device_ids.id,
                    #'under_warranty': True
                })
                _logger.warning('self.destination_device_ids.id: %s', self.destination_device_ids.id)
                subscription.message_post(body=repair_internal_notes, body_is_html=True)

            # Comments to log on the operation log comment
            repair_internal_notes = repair_internal_notes.replace("RMA_ODT", nodt_link)
            operation_log_comment = operation_log_comment.replace("RMA_ODT", nodt_link)
            operation_log_comment = operation_log_comment.replace("SUSTITUIDO", replaced_device_link)
            operation_log_comment = operation_log_comment.replace('EQUIPO', new_device_link)
            operation_log_comment = operation_log_comment.replace('RELATED_ODT', fsm_service_link)

            # We update replaced device data
            values = {
                'administrative_status': "rma",
                'stage_id': stage_rma_status.id
            }
            self.do_device_operation(device, operation_log_comment, stage_rma_status, values)

            operation_log_comment_device = operation_log_comment_device.replace('EQUIPO', replaced_device_link)
            operation_log_comment_device = operation_log_comment_device.replace('SUSTITUIDO', new_device_link)
            operation_log_comment_device = operation_log_comment_device.replace('RMA_ODT', nodt_link)

            values = {
                'administrative_status': "replacement",
                'client_id': client_id.id,
                'stage_id': replacement_status.id,
            }
            self.do_device_operation(self.destination_device_ids, operation_log_comment_device, replacement_status, values)
            self.create_device_log(device, operation_log_comment)
            self.log_to_channel(channel_id, operation_log_comment, nodt)

        # Check mandatory fields
        return {}

    def execute_loan_substitution(self):
        # We get selected Ids that we'll process for hibernation
        active_model = self._context.get('active_model')
        active_records = self.env[active_model].browse(self._context.get('active_ids'))

        # Get global configuration object to retrieve options from settings
        lgps_config = self.sudo().env['ir.config_parameter']

        # Check mandatory fields
        self._check_mandatory_fields(['comment', 'related_field_service'])

        channel_id = lgps_config.get_param('lgps.device_wizard.substitution_default_channel')
        if not channel_id:
            raise UserError(_(
                'There is not configuration for default channel.\n '
                'Configure this in order to send the notification.'
            ))

        replacement_status = self.env.ref('lgps.stage_installed')
        stage_rma_status = self.env.ref('lgps.stage_rma')

        body_title = "<b class='text-info'>[Proceso de Sustitución por Comodato]</b><br/><br/>"
        # Messages to Log on Models
        repair_internal_notes = body_title
        repair_internal_notes += 'El equipo SUSTITUIDO se sustituyó con el equipo: EQUIPO durante la atención'
        repair_internal_notes += ' del servicio: RELATED_ODT<br/>'

        operation_log_comment = body_title
        operation_log_comment += 'El equipo SUSTITUIDO se retira mientras que esta en revisión con número de reparación'
        operation_log_comment += ' RMA_ODT  <br/><br/> Se instala el equipo EQUIPO en su lugar durante la atención del'
        operation_log_comment += ' servicio RELATED_ODT <br/><br/>'
        operation_log_comment += 'Se entrega equipo al área de calidad para revisión.<br/><br/>'
        operation_log_comment += 'Comentario: ' + self.comment

        operation_log_comment_device = body_title
        operation_log_comment_device += 'Se instala el equipo SUSTITUIDO como sustituto de EQUIPO mientras está en '
        operation_log_comment_device += 'revisión con número de  reparación RMA_ODT <br/><br/>'
        operation_log_comment_device += 'Comentario: ' + self.comment

        for device in active_records:
            if not device.warranty_start_date:
                raise UserError(_(
                    'The device does not have Warranty Start Date. \n'
                    'Complete this first in order to process the Substitution Operation.'
                ))
            _logger.warning('device.administrative_status: %s', device.administrative_status)
            if device.administrative_status != 'comodato':
                raise UserError(
                    _('The device is not classified as Comodato. \n This operationa cannot be completed.')
                )

            # We take original values from removed device
            client_id = device.client_id
            assigned_to = lgps_config.get_param('lgps.device_wizard.repairs_default_user')
            replaced_device_link = device._get_html_link()
            new_device_link = self.destination_device_ids._get_html_link()
            fsm_service_link = self.related_field_service._get_html_link()

            repair_internal_notes = repair_internal_notes.replace("SUSTITUIDO", replaced_device_link)
            repair_internal_notes = repair_internal_notes.replace("EQUIPO", new_device_link)
            repair_internal_notes = repair_internal_notes.replace("RELATED_ODT", fsm_service_link)

            nodt = self.create_repair_record(device, assigned_to)
            nodt_link = nodt._get_html_link()
            _logger.warning('nodt: %s', nodt)

            # We are goint to look for the removed device subscription to update to installed device
            subscription = self.env['sale.order'].search([
                ['device_id', '=', device.id],
                ['subscription_state', '=', '3_progress']
            ])

            if subscription:
                subscription.write({'device_id': self.destination_device_ids.id})
                _logger.warning('self.destination_device_ids.id: %s', self.destination_device_ids.id)
                subscription.message_post(body=repair_internal_notes, body_is_html=True)

            # Comments to log on the operation log comment
            repair_internal_notes = repair_internal_notes.replace("RMA_ODT", nodt_link)
            operation_log_comment = operation_log_comment.replace("RMA_ODT", nodt_link)
            operation_log_comment = operation_log_comment.replace("SUSTITUIDO", replaced_device_link)
            operation_log_comment = operation_log_comment.replace('EQUIPO', new_device_link)
            operation_log_comment = operation_log_comment.replace('RELATED_ODT', fsm_service_link)

            # We update replaced device data
            values = {
                'administrative_status': "rma",
                'stage_id': stage_rma_status.id
            }
            self.do_device_operation(device, operation_log_comment, stage_rma_status, values)

            operation_log_comment_device = operation_log_comment_device.replace('EQUIPO', replaced_device_link)
            operation_log_comment_device = operation_log_comment_device.replace('SUSTITUIDO', new_device_link)
            operation_log_comment_device = operation_log_comment_device.replace('RMA_ODT', nodt_link)

            values = {
                'administrative_status': "comodato",
                'client_id': client_id.id,
                'stage_id': replacement_status.id,
            }
            self.do_device_operation(self.destination_device_ids, operation_log_comment_device, replacement_status,
                                     values)
            self.create_device_log(device, operation_log_comment)
            self.log_to_channel(channel_id, operation_log_comment, nodt)

        return {}

    def execute_add_reactivate(self):
        body = ''
        notify_gps_list = ''
        active_records = self.return_active_records()
        installed_status = self.env.ref('lgps.stage_installed')

        # LGPS Global Configuration
        lgps_config = self.sudo().env['ir.config_parameter']

        channel_id = lgps_config.get_param('lgps.add_reactivation_device_wizard.default_channel')
        if not channel_id:
            raise UserError(_(
                'There is not configuration for default channel.\n Configure this in order to send the notification.'))

        for r in active_records:
            acumulador = ""
            body = "[Proceso de Alta/Reactivación]<br/><br/>" + self.comment + '<br/>'
            gps_functions_summary = "<hr/>Se activan las funciones de:<br/><br/>"
            additional_functions = False
            reactivation_reason = dict(self._fields['reactivation_reason']._description_selection(self.env)).get(
                self.reactivation_reason)

            platform = self.platform_list_id.name if self.platform_list_id.name else 'Sin Plataforma'
            client = r.client_id.name if r.client_id else 'Sin Cliente'
            equipo = r.name
            nick = r.nick if r.nick else 'NA'

            acumulador += '<br/><b>Plataforma:</b> ' + platform
            acumulador += '<br/><b>Cliente:</b> ' + client
            acumulador += '<br/><b>Solicitado Por:</b> ' + self.requested_by
            acumulador += '<br/><b>Motivo:</b> ' + reactivation_reason
            acumulador += '<br/><b>Equipo:</b> ' + equipo
            # acumulador += '<br/><b>Nick:</b> ' + nick
            if self.cell_chip_id:
                acumulador += '<br/><b>Línea Asignada:</b> ' + self.cell_chip_id.name

            notify_gps_list += '<br/>' + client + ' || ' + equipo + ' || ' + nick + ' || ' + platform
            if self.tracking:
                additional_functions = True
                gps_functions_summary += "Rastreo<br/>"
            if self.fuel:
                additional_functions = True
                gps_functions_summary += "Combustible<br/>"
            if self.fuel_hall:
                additional_functions = True
                gps_functions_summary += "Combustible Efecto Hall<br/>"
            if self.scanner:
                additional_functions = True
                gps_functions_summary += "Escánner<br/>"
            if self.temperature:
                additional_functions = True
                gps_functions_summary += "Temperatura<br/>"
            if self.logistic:
                additional_functions = True
                gps_functions_summary += "Logística<br/>"
            if self.collective:
                additional_functions = True
                gps_functions_summary += "Colectivos Boson<br/>"
            if self.fleetrun:
                additional_functions = True
                gps_functions_summary += "Mantenimiento de Flotilla<br/>"

            body += '<br/>' + acumulador
            if additional_functions:
                body += gps_functions_summary

            # Activando el equipo
            r.write({
                'fuel': self.fuel if self.fuel else r.fuel,
                'fuel_hall': self.fuel_hall if self.fuel_hall else r.fuel_hall,
                'scanner': self.scanner if self.scanner else r.scanner,
                'temperature': self.temperature if self.temperature else r.temperature,
                'logistic': self.logistic if self.logistic else r.logistic,
                'collective': self.collective if self.collective else r.collective,
                'tracking': self.tracking if self.tracking else r.tracking,
                'fleetrun': self.fleetrun if self.fleetrun else r.fleetrun,
                'platform_list_id': self.platform_list_id.id if self.platform_list_id else None,
                'cell_chip_id': self.cell_chip_id.id if self.cell_chip_id else None,
                'stage_id': installed_status.id,
            })
            # write Comment
            r.message_post(body=body)
            self.create_device_log(r, body)

            channel_msn = '<br/>Los equipos mencionados a continuación se procesaron para Alta/Reactivación por motivo de:<br/>'
            channel_msn += self.comment + '<br/> soliciato por: ' + self.requested_by + '<br/>'
            channel_msn += notify_gps_list

            self.log_to_channel(channel_id, channel_msn)

        return {}

    # ############################################# HELP FUNCTIONS ###################################################
    def return_active_records(self):
        active_model = self._context.get('active_model')
        active_records = self.env[active_model].browse(self._context.get('active_ids'))
        return active_records

    def chek_status_before_further_process(self, devices, status):
        error = False
        buffer = ''

        for device in devices:
            if device.stage_id.id != status.id:
                error = True
                buffer += device.name + '  /  ' + device.state + '  /  ' + device.platform_list_id.name + '\n'

        if error:
            raise UserError(
                _('Some devices does not has the right status for this operation.\n\n ' + buffer)
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
        odt_object = self.env['lgps.rma_process']
        odt = odt_object.create(dictionary)
        return odt

    def copy_subscription(self, original, default_values):
        subscription_copy = original.copy(default=default_values)
        _logger.warning('subscription_copy: %s', subscription_copy)
        return subscription_copy

    def _check_mandatory_fields(self, rules):
        for rule in rules:

            if not getattr(self, rule):
                raise UserError(self._get_error_message_for_field(rule))

    def _get_error_message_for_field(self, field=''):
        if field == 'comment':
            return _('You forgot to comment the reason for this process to run.')
        if field == 'requested_by':
            return _('Who authorizes this request?')
        if field == 'related_field_service':
            return _('You forgot to select the Related Field Service')

    def _change_subscriptions_stage(self, subscriptions, comment=None, default_stage=None):
        close = False
        close_stage = '6_churn'
        new_stage = default_stage if default_stage else close_stage

        for subscription in subscriptions:
            subscription.write({'subscription_state': new_stage})

            if close:
                if comment:
                    body = 'Se cierra suscripción por motivo de: <br>' + comment
                else:
                    body = 'Se cierra suscripción por motivo de: <br>'
            else:
                body = comment

            subscription.message_post(body=body, body_is_html=True)

        return True

    def create_device_log(self, device, log_comment="", nodt=None):
        log_object = self.env['lgps.device_history']
        repar_id = nodt.id if nodt else None

        dictionary = {
            'name': device.name + ' - ' + self.operation_mode,
            'product_id': device.product_id.id,
            'serial_number_id': device.serial_number_id.id,
            'client_id': device.client_id.id,
            'device_ids': device.id,
            'destination_device_ids': self.destination_device_ids.id,
            'operation_mode': self.operation_mode,
            'related_odt': repar_id,
            'related_service': self.related_field_service.id,
            'requested_by': self.requested_by,
            'comment': self.comment,
            'reason': self.reason,
            'log_msn': log_comment
        }
        device_log = log_object.create(dictionary)
        return device_log

    def log_to_channel(self, channel_id, channel_msn):
        _logger.warning('Trying to log to channel: %s', channel_id)
        if not channel_id:
           raise UserError(
               _('There is not configuration for default channel.\n Configure this in order to send the notification.')
           )
        else:
            channel_notifier = self.sudo().env['discuss.channel'].search([('id', '=', channel_id)])
            _logger.warning('channel_notifier: %s', channel_notifier)
            channel_notifier.with_user(self.env.user).message_post(
                body=channel_msn,
                subtype_xmlid='mail.mt_note',
                message_type='comment',
                body_is_html=True
            )

        return {}

    def set_cellchips_to_deactivate(self, cellchips_list):
        chips = self.sudo().env['lgps.cellchip'].search([('id', 'in', cellchips_list)])
        for chip in chips:
            chip.write({
                'name': chip.name + 'B',
                'to_deactivate': True,
            })

    def inspect_device_functions(self, device, inverse_check=False):

        gps_functions_summary = ''
        additional_functions = False
        search_object = self if inverse_check else device
        msn_text = 'activaron' if inverse_check else 'desactivaron'
        # To do, find and elgant way to walk through properties depende the object to inspect
        #
        # properties_list = {
        #     'tracking': 'Rastero',
        #     'fuel': 'Combustible',
        #     'fuel_hall': 'Combustible Efecto Hall',
        #     'scanner': 'Escánner',
        #     'temperature': 'Temperatura',
        #     'logistic': 'Logística',
        #     'collective': 'Colectivos Boson',
        #     'fleetrun': 'Mantenimiento de Flotilla',
        # }
        #
        # _logger.warning('properties_list: %s', properties_list)
        # _logger.warning('search_object: %s', search_object)
        #
        # for k, v in properties_list.items():
        #     _logger.warning('k: %s', k)
        #     _logger.warning('v: %s', v)
        #     thing = getattr(search_object, k, False)
        #     _logger.warning('found thing: %s', k, thing)
        #
        #     if search_object.thing:
        #         additional_functions = True
        #         gps_functions_summary += "<li>"+v+"</li>"
        #
        #
        # _logger.warning('additional_functions: %s', additional_functions)

        if search_object.tracking:
            additional_functions = True
            gps_functions_summary += "<li>Rastreo</li>"
        if search_object.fuel:
            additional_functions = True
            gps_functions_summary += "<li>Combustible</li>"
        if search_object.fuel_hall:
            additional_functions = True
            gps_functions_summary += "<li>Combustible Efecto Hall</li>"
        if search_object.scanner:
            additional_functions = True
            gps_functions_summary += "<li>Escánner</li>"
        if search_object.temperature:
            additional_functions = True
            gps_functions_summary += "<li>Temperatura</li>"
        if search_object.logistic:
            additional_functions = True
            gps_functions_summary += "<li>Logística</li>"
        if search_object.collective:
            additional_functions = True
            gps_functions_summary += "<li>Colectivos Boson</li>"
        if search_object.fleetrun:
            additional_functions = True
            gps_functions_summary += "<li>Mantenimiento de Flotilla</li>"

        if additional_functions:
            summary = "<hr/>Se " + msn_text + " las funciones de:<br/><ul>" + gps_functions_summary + "</ul>"
        else:
            summary = "<hr/>No se " + msn_text + " funciones en el dispositivo.<br/><br/>"

        return summary

    def do_device_operation(self, device, log_body, new_stage, vals=None):

        _logger.warning('device: %s', device)
        _logger.warning('log_body: %s', log_body)
        _logger.warning('new_stage: %s', new_stage)
        _logger.warning('vals: %s', vals)

        if not vals:
            device.write({
                'fuel': False,
                'fuel_hall': False,
                'scanner': False,
                'temperature': False,
                'logistic': False,
                'collective': False,
                'tracking': True,
                'fleetrun': False,
                'electronics': False,
                'stage_id': new_stage.id
            })
        else:
            device.write(vals)
        # Post Log Note to Record
        device.message_post(body=log_body, body_is_html=True)

    def create_repair_record(self, device, assigned_to):
        repair_name = self.env['ir.sequence'].sudo().next_by_code('repair.order')
        repair_object = self.env['repair.order']
        dictionary = {
            'name': repair_name,
            'state': 'draft',
            'partner_id': device.client_id.id,
            'product_id': device.product_id.id,
            'lot_id':device.serial_number_id.id,
            'user_id': assigned_to,
        }

        repair = repair_object.create(dictionary)
        return repair

    def stop_execution(self, msn="Stop execution"):
        raise UserError(msn)
