# -*- coding: utf-8 -*-
{
    'name': 'lgps',
    'description': 'Intralix module for internal processes',
    'author': 'Intralix',
    'application': True,
    'website': 'https://www.intralix.com',
    'category': 'Uncategorized',
    'version': '0.0.6',
    'depends': [
        'base',
        'stock',
        'contacts',
        'account',
        'repair',
        'crm',
        'sale_subscription',
        'helpdesk',
        'mail',
        'project',
        'sale',
        'industry_fsm',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/devices_common_operations.xml',
        'views/main_menu.xml',
        'views/res_config_settings_views.xml',
        'reports/subscription_details.xml',
        'views/accessory.xml',
        'views/cellchip.xml',
        'views/platform_list.xml',
        'views/device.xml',
        'views/accessory_history.xml',
        'views/custom_subscription.xml',
        'views/tracking.xml',
        'views/tracking_logs.xml',
        'views/custom_partner.xml',
        'views/custom_fsm.xml',
        'views/custom_help_desk.xml',
        'views/device_history.xml',
        'views/custom_invoice.xml',
    ],
}
