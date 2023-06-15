# -*- coding: utf-8 -*-
#import pika  # Library RabbitMQ
import json
import time
from datetime import timedelta
from odoo import api, models, fields, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class CommonDevicesOperationsWizard(models.TransientModel):
    _name = "lgps.device_operations"
    _description = "Common Operations To Devices Wizard"

    def _default_gpsdevices(self):
        return self.env['lgps.device'].browse(self._context.get('active_ids'))

    operation_mode = fields.Selection(
        [
            ('drop', _('Baja de Equipos')),
            ('hibernation', _('Hibernación de Equipos')),
            ('wakeup', _('Deshibernación de Equipos')),
            ('replacement', _('Reemplazo de equipo por garantía')),
            ('substitution', _('Sustitución de equipo por revisión')),
            ('add_reactivate', _('Alta / Reactivación Equipo')),
            ('loan_substitution', _('Reemplazo de Comodato'))
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

    gpsdevice_ids = fields.Many2many(
        comodel_name='lgps.device',
        string="Gps Device",
        required=True,
        default=_default_gpsdevices,
    )

    destination_gpsdevice_ids = fields.Many2one(
        comodel_name='lgps.device',
        string=_("Substitute equipment"),
        domain="["
               "('status', 'in', ['installed', 'demo', 'comodato', 'borrowed','replacement']),"
               "('platform_list_id', '!=', 'Drop')"
               "]"
    )

    related_odt = fields.Many2one(
        comodel_name='repair.order',
        string=_("Work order related"),
    )

    related_field_service = fields.Many2one(
        comodel_name="project.task",
        string=_("Related work order")
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

    # Available services
    tracking = fields.Boolean(default=False, string=_("Tracking"))
    fuel = fields.Boolean(default=False, string=_("Fuel"))
    fuel_hall = fields.Boolean(default=False, string=_("Efecto Hall"))
    scanner = fields.Boolean(default=False, string="Scanner")
    temperature = fields.Boolean(default=False, string=_("Temperature"))
    logistic = fields.Boolean(default=False, string=_("Logistic"))
    collective = fields.Boolean(default=False, string=_("Collective"))
    fleetrun = fields.Boolean(default=False, string=_("Fleetrun"))
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
            raise UserError('El proceso de reemplazo esta siendo revisado por lo que no esta disponible')
            #self.execute_replacement()
        # Substitution
        if self.operation_mode == 'substitution':
            raise UserError('El proceso de sustitución esta siendo revisado por lo que no esta disponible')
            #self.execute_substitution()
        # Wakeup
        if self.operation_mode == 'wakeup':
            # raise UserError('El proceso de deshibernación esta siendo revisado por lo que no esta disponible')
            self.execute_wakeup()
        # Reactivate
        if self.operation_mode == 'add_reactivate':
            raise UserError('El proceso de reactivación esta siendo revisado por lo que no esta disponible')
            #self.execute_add_reactivate()
        # Loan Substitution
        if self.operation_mode == 'loan_substitution':
            raise UserError('El proceso de reemplazo por sustitución esta siendo revisado por lo que no esta disponible')
            #self.execute_loan_substitution()

        # self.publishMessageToQueue()
        return {}

    def execute_deactivation(self):
        # We get the seleteced Ids
        active_model = self._context.get('active_model')
        active_records = self.env[active_model].browse(self._context.get('active_ids'))
        drop_platform = self.env['lgps.platform_list'].search([['name', '=', 'Sin Plataforma']], limit=1)

        # Buffer Vars
        cellchips_ids = []
        notify_cellchisp_list = ""
        notify_gps_list = ""
        requested_by = self.requested_by

        # for each selected record, we are going to make some operations:
        for r in active_records:
            body = "[Proceso de Baja]<br/><br/>" + self.comment + '<br/>'
            gps_functions_summary = "<hr/>Se desactivaron las funciones de:<br/><br/>"
            acumulador = ""
            additional_functions = False

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
                notify_cellchisp_list += '<br/>' + r.cell_chip_id.name + ' - ' + r.cell_chip_id.provider

            notify_gps_list += '<br/>' + client + ' || ' + equipo + ' || ' + nick + ' || ' + platform

            # Comprobando funciones adicionales
            if r.tracking:
                additional_functions = True
                gps_functions_summary += "Rastreo<br/>"
            if r.fuel:
                additional_functions = True
                gps_functions_summary += "Combustible<br/>"
            if r.fuel_hall:
                additional_functions = True
                gps_functions_summary += "Combustible Efecto Hall<br/>"
            if r.scanner:
                additional_functions = True
                gps_functions_summary += "Escánner<br/>"
            if r.temperature:
                additional_functions = True
                gps_functions_summary += "Temperatura<br/>"
            if r.logistic:
                additional_functions = True
                gps_functions_summary += "Logística<br/>"
            if r.collective:
                additional_functions = True
                gps_functions_summary += "Colectivos Boson<br/>"
            if r.fleetrun:
                additional_functions = True
                gps_functions_summary += "Mantenimiento de Flotilla<br/>"

            body += '<br/>' + acumulador
            if additional_functions:
                body += gps_functions_summary

            # odoobot = self.env.ref("base.partner_root")
            # r.message_post(author_id=odoobot.id, body=body)
            r.message_post(body=body)
            # Create Object Log
            self.create_device_log(r, body)

        # Ejecutamos la Baja en el sistema
        active_records.write({
            'tracking': False,
            'fuel': False,
            'fuel_hall': False,
            'scanner': False,
            'temperature': False,
            'logistic': False,
            'collective': False,
            'fleetrun': False,
            'platform_list_id': drop_platform.id,
            # 'notify_offline': False,
        })

        self.cellchips_list = notify_cellchisp_list
        self.devices_list = notify_gps_list

        # We are going to look for the subscription and make some changes
        subscriptions = self.env['sale.subscription'].search([['device_id', 'in', active_records.ids]])
        if subscriptions:
            self._change_subscriptions_stage(subscriptions, "El equipo se ha dado de baja en el sistema.")

        # Log para Internos
        channel_msn = '<br/>Los equipos listados a continuación se procesaron para dar de baja por motivo de:<br/>'
        channel_msn += self.comment + '<br/>'
        channel_msn += self.devices_list
        channel_msn += '<br/><br/>Favor de ejecutar la baja la siguientes líneas:<br/>'
        channel_msn += self.cellchips_list

        # Log to Channel
        # Deactivated due to use and some error that is hard to track to resolve
        lgps_config = self.sudo().env['ir.config_parameter']
        channel_id = lgps_config.get_param('lgps.device_wizard.drop_default_channel')
        self.log_to_channel(channel_id, channel_msn)

        return {}

    def execute_hibernation(self):
        # raise UserError(_('Mensaje de pruebas para detener la ejecuión del código'))

        # We get selected Ids that we'll process for hibernation
        active_model = self._context.get('active_model')
        active_records = self.env[active_model].browse(self._context.get('active_ids'))

        # Get global configuration object to retrieve options from settings
        lgps_config = self.sudo().env['ir.config_parameter']

        # We get all configuration parameters
        channel_id = lgps_config.get_param('lgps.hibernate_device_wizard.default_channel')
        subscription_close_stage = self.sudo().env.ref('sale_subscription.sale_subscription_stage_closed')
        subscription_hibernate_stage_id = lgps_config.get_param('lgps.device_wizard.hibernate_default_subscription_stage')
        subscription_current_hibernate_stage_id = lgps_config.get_param('lgps.device_wizard.hibernate_current_subscription_stage')
        subscription_hibernate_template_id = lgps_config.get_param('lgps.device_wizard.hibernate_default_subscription_template')
        hibernation_commercial_id = lgps_config.get_param('lgps.device_wizard.hibernate_commercial_default')
        hibernate_user_id = lgps_config.get_param('lgps.device_wizard.hibernate_user_default')
        hibernate_price_list_id = lgps_config.get_param('lgps.device_wizard.hibernate_default_price_list_id')
        hibernate_product_id = lgps_config.get_param('lgps.device_wizard.hibernate_default_service')

        if not hibernate_product_id:
            raise UserError(_(
                'There is not configuration for default service.'
                '\n Configure this in order to create subscription successfully.'))
        else:
            product = self.sudo().env['product.product'].search([('id', '=', hibernate_product_id)], limit=1)

        # Buffer Vars
        notify_gps_list = ""
        skip_subscription_ids = []

        # Procesamos los quipos seleccionados:
        for r in active_records:
            body = "[Proceso de Hibernación]<br/><br/>"
            body += self.comment + '<br/><b>Solicitado por</b>: '
            body += self.requested_by + '<br/>'
            gps_functions_summary = "<hr/>Se desactivaron las funciones de:<br/><br/>"
            acumulador = ""
            additional_functions = False

            platform = r.platform_list_id.name if r.platform_list_id.name else 'Sin Plataforma'
            chip = r.cell_chip_id.name if r.cell_chip_id else 'Sin chip'
            client = r.client_id.name if r.client_id else 'Sin Cliente'
            equipo = r.name
            nick = r.nick if r.nick else 'NA'

            acumulador += '<br/><b>Plataforma:</b> ' + platform
            acumulador += '<br/><b>Cliente:</b> ' + client
            acumulador += '<br/><b>Equipo:</b> ' + equipo
            acumulador += '<br/><b>Nick:</b> ' + nick
            acumulador += '<br/><b>Línea:</b> ' + chip

            notify_gps_list += '<br/>' + client + ' || ' + equipo + ' || ' + nick + ' || ' + platform

            # Comprobando funciones adicionales
            if r.fuel:
                additional_functions = True
                gps_functions_summary += "Combustible<br/>"
            if r.fuel_hall:
                additional_functions = True
                gps_functions_summary += "Combustible Efecto Hall<br/>"
            if r.scanner:
                additional_functions = True
                gps_functions_summary += "Escánner<br/>"
            if r.temperature:
                additional_functions = True
                gps_functions_summary += "Temperatura<br/>"
            if r.logistic:
                additional_functions = True
                gps_functions_summary += "Logística<br/>"
            if r.collective:
                additional_functions = True
                gps_functions_summary += "Colectivos Boson<br/>"
            if r.fleetrun:
                additional_functions = True
                gps_functions_summary += "Mantenimiento de Flotilla<br/>"

            body += '<br/>' + acumulador
            if additional_functions:
                body += gps_functions_summary

            # Desactivamos funciones e hibernamos
            r.write({
                'fuel': False,
                'fuel_hall': False,
                'scanner': False,
                'temperature': False,
                'logistic': False,
                'collective': False,
                'tracking': True,
                'fleetrun': False,
                'status': "hibernate",
                # 'notify_offline': False,
            })

            r.message_post(body=body)
            self.create_device_log(r, body)

            # Revisamos el tema de las suscripciones:
            default = dict(None or {})
            new_subscription = self.env['sale.subscription']

            if not subscription_hibernate_template_id:
                self.message_post(
                    body="<b style='color:red'>AVISO</b>"
                         "<br>No se pudo crear la subscripción de Hibernación automáticamente en el equipo."
                         "<br>Deberá crearla manualmente."
                         "<br>Es probable que ninguna plantilla de subscripción esta activa.")
            else:
                n = new_subscription.create({
                    'name': 'New Subscription',
                    'code': 'Hibernación ' + r.name,
                    'stage_id': int(subscription_hibernate_stage_id),
                    'template_id': int(subscription_hibernate_template_id),
                    'pricelist_id': int(hibernate_price_list_id),
                    'partner_id': int(r.client_id.id),
                    'device_id': r.id,
                    'user_id': int(hibernate_user_id),
                    'team_id': int(hibernation_commercial_id),
                    'recurring_invoice_line_ids': [(0, 0, {
                        'product_id': product.id,
                        'quantity': 1,
                        'uom_id': product.uom_id.id,
                        'price_unit': self.get_price_from_pricelist(hibernate_price_list_id, product),
                        'name': product.display_name,
                        'discount': 0,
                    })]
                })

                skip_subscription_ids.append(n.id)
                # raise UserError(_('Mensaje de pruebas para detener la ejecuión del código'))
        self.devices_list = notify_gps_list
        # Alterando las suscripciones encontradas
        subscriptions = self.env['sale.subscription'].search([
            ['device_id', 'in', active_records.ids],
            ['id', 'not in', skip_subscription_ids],
            ['stage_id', '!=', subscription_close_stage.id],
        ])

        # Alterando las suscripciones
        if subscriptions:
            self._change_subscriptions_stage(
                subscriptions,
                "El equipo se ha procesado como Hibernado en el sistema.",
                subscription_current_hibernate_stage_id
            )

        #Log Channel
        channel_msn = '<br/>Los equipos mencionados a continuación se procesaron para ser hibernados por motivo de:<br/>'
        channel_msn += self.comment + '<br/> soliciato por: ' + self.requested_by + '<br/>'
        channel_msn += self.devices_list

        # Send Message
        self.log_to_channel(channel_id, channel_msn)
        return {}

    def execute_replacement(self):
        return {}

    def execute_substitution(self):
        # Check mandatory fields
        return {}

    def execute_wakeup(self):
        body = ''
        notify_gps_list = ''

        active_records = self.return_active_records()
        self.chek_status_before_further_process(active_records, 'hibernate')

        # LGPS Global Configuration
        lgps_config = self.sudo().env['ir.config_parameter']

        subscription_hibernate_stage_id = lgps_config.get_param(
            'lgps.device_wizard.hibernate_current_subscription_stage')
        if not subscription_hibernate_stage_id:
            raise UserError(_(
                'There is not configuration for default current subscriptions stage.\n'
                'Configure this in order to send the notification.'))

        channel_id = lgps_config.get_param('lgps.hibernate_device_wizard.default_channel')
        if not channel_id:
            raise UserError(_(
                'There is not configuration for default channel.\n Configure this in order to send the notification.'))

        subscription_in_progress_stage = self.sudo().env.ref('sale_subscription.sale_subscription_stage_in_progress')
        subscription_hibernate_stage_id = self.sudo().env['sale.subscription.stage'].search([
            ('id', '=', subscription_hibernate_stage_id)], limit=1)

        # Procesamos los quipos seleccionados:
        for r in active_records:
            acumulador = ""
            body = "[Proceso de Deshibernación]<br/><br/>" + self.comment + '<br/>'
            body += '<br/><b>Solicitado por</b>: '
            body += self.requested_by + '<br/>'
            gps_functions_summary = "<hr/>Se activan las funciones de:<br/><br/>"
            additional_functions = False

            platform = r.platform_list_id.name if r.platform_list_id.name else 'Sin Plataforma'
            client = r.client_id.name if r.client_id else 'Sin Cliente'
            equipo = r.name
            nick = r.nick if r.nick else 'NA'

            acumulador += '<br/><b>Plataforma:</b> ' + platform
            acumulador += '<br/><b>Cliente:</b> ' + client
            acumulador += '<br/><b>Solicitado Por:</b> ' + self.requested_by
            acumulador += '<br/><b>Equipo:</b> ' + equipo
            acumulador += '<br/><b>Nick:</b> ' + nick
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
                'status': self.device_status,
                # 'notify_offline': True,
            })
            # write Comment
            r.message_post(body=body)

            # Buscamos las suscripciones que estén en el estatus marcado para hibernación y las pasamos a progreso
            hibernated_subscriptions = self.env['sale.subscription'].search([
                ['device_id', '=', r.id],
                ['stage_id', '=', subscription_hibernate_stage_id.id]
            ])
            # _logger.warning('subscription_hibernate_stage_id: %s', subscription_hibernate_stage_id)
            # _logger.warning('hibernated_subscriptions: %s', hibernated_subscriptions)

            # Buscamos la suscripción que este en progreso y la pasamos a cerrada
            in_progress_subscriptions = self.env['sale.subscription'].search([
                ['device_id', '=', r.id],
                ['stage_id', '=', subscription_in_progress_stage.id]
            ])

            # _logger.warning('in_progress_subscriptions: %s', in_progress_subscriptions)
            if in_progress_subscriptions:
                self._change_subscriptions_stage(in_progress_subscriptions,
                                                 "El equipo se ha deshibernado en el sistema.")

            if hibernated_subscriptions:
                self._change_subscriptions_stage(
                    subscriptions=hibernated_subscriptions,
                    comment="Se reactiva la suscripción por que el equipo fue deshibernado en el sistema",
                    default_stage=subscription_in_progress_stage
                )
            # Create Object Log
            self.create_device_log(r, body)

        channel_msn = '<br/>Los equipos mencionados a continuación se procesaron para ser deshibernados por motivo de:<br/>'
        channel_msn += self.comment + '<br/> soliciato por: ' + self.requested_by + '<br/>'
        channel_msn += notify_gps_list

        self.log_to_channel(channel_id, channel_msn)

        return {}

    def execute_add_reactivate(self):
        return {}

    def execute_loan_substitution(self):
        return {}

    def return_active_records(self):
        active_model = self._context.get('active_model')
        active_records = self.env[active_model].browse(self._context.get('active_ids'))

        return active_records

    def chek_status_before_further_process(self, devices, status):
        error = False
        buffer =''

        for device in devices:
            if device.status != status or device.platform_list_id.name == 'Drop':
                error = True
                buffer += device.name + '  /  ' + device.status + '  /  ' + device.platform_list_id.name + '\n'

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
        odt_object = self.env['repair.order']
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
        if field == 'related_odt':
            return _('You forgot to select the Related ODT')

    def _change_subscriptions_stage(self, subscriptions, comment=None, default_stage=None):
        close = False

        if not default_stage:
            close = True
            subscription_close_stage = self.sudo().env.ref('sale_subscription.sale_subscription_stage_closed')
        else:
            if isinstance(default_stage, str):
                subscription_close_stage = self.sudo().env['sale.subscription.stage'].search([
                    ('id', '=', default_stage)], limit=1)
            else:
                subscription_close_stage = default_stage

        for subscription in subscriptions:
            subscription.write({'stage_id': subscription_close_stage.id})
            if close:
                if comment:
                    body = 'Se cierra suscripción por motivo de: <br>' + comment
                else:
                    body = 'Se cierra suscripción por motivo de: <br>'
            else:
                body = comment

            subscription.message_post(body=body)

        return True

    def create_device_log(self, device, log_comment=""):
        log_object = self.env['lgps.device_history']

        dictionary = {
            'name': device.name + ' - ' + self.operation_mode,
            'product_id': device.product_id.id,
            'serial_number_id': device.serial_number_id.id,
            'client_id': device.client_id.id,
            'gpsdevice_ids': device.id,
            'destination_gpsdevice_ids': self.destination_gpsdevice_ids.id,
            'operation_mode': self.operation_mode,
            'related_odt': self.related_odt.id,
            'requested_by': self.requested_by,
            'comment': self.comment,
            'reason': self.reason,
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
            channel_notifier = self.sudo().env['mail.channel'].search([('id', '=', channel_id)])
            channel_notifier.with_user(self.env.user).message_post(body=channel_msn)

        return {}

    def cool_format(self, data):
        buffer = ''
        col_width = max(len(word) for row in data for word in row) + 4  # padding
        for row in data:
            buffer += "".join(word.ljust(col_width) for word in row) + '\n'
        _logger.warning('buffer: %s', buffer)

        return buffer
