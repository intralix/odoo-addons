# -*- coding: utf-8 -*-
{
    'name': 'lgps',
    'description': 'Intralix module for internal processes',
    'author': 'Intralix',
    'application': True,
    'website': 'https://www.intralix.com',
    'category': 'Uncategorized',
    'version': '0.0.0',
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
        'sale'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/main_menu.xml',
        'views/accessory.xml',
        'views/cellchip.xml',
    ],
}
