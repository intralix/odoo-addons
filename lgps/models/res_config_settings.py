# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    deactivation_channel_id = fields.Many2one(
        comodel_name='discuss.channel',
        string=_("Default Deactivations Channel"),
        config_parameter='lgps.deactivation_device.default_channel',
    )

    deactivation_state = fields.Char(
        string=_('Device Deactivation State'),
        readonly=True,
        default="disconnected",
        config_parameter='lgps.device_deactivation_state',
    )

    hibernate_channel_id = fields.Many2one(
        comodel_name='discuss.channel',
        string=_("Default Hibernate Channel"),
        config_parameter='lgps.hibernate_device_wizard.default_channel',
    )

    subscription_hibernation_closed_state = fields.Char(
        string=_('Subscription Closed State'),
        readonly=True,
        default="6_churn",
        config_parameter='lgps.close_subscription.default_state',
    )

    subscription_hibernation_state = fields.Char(
        string=_('Subscription Hibernation State'),
        readonly=True,
        default="4_paused",
        config_parameter='lgps.hibernate_subscription.default_state',
    )

    substitution_channel_id = fields.Many2one(
        comodel_name='discuss.channel',
        string=_("Default Substitution Channel"),
        config_parameter='lgps.device_wizard.substitution_default_channel',
    )

    repairs_assigned_user_id = fields.Many2one(
        comodel_name='res.users',
        string=_("Assign Repairs to this users"),
        config_parameter='lgps.device_wizard.repairs_default_user',
    )

    reactivation_channel_id = fields.Many2one(
        comodel_name='discuss.channel',
        string=_("Default Reactivation Channel"),
        config_parameter='lgps.add_reactivation_device_wizard.default_channel',
    )

