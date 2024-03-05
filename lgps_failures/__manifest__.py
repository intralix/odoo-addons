# -*- coding: utf-8 -*-
{
    'name': 'lgps_failures',
    'description': 'Intralix module for track faluires',
    'author': 'Intralix',    
    'website': 'https://www.intralix.com',
    'category': 'Uncategorized',
    'version': '0.0.5',
    'depends': [
        'base',
        'lgps'        
    ],    
    'data': [        
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/failures_menu.xml',
        'views/custom_repair.xml',
        'views/failures_list.xml',
        'views/failures_categories_list.xml',
        'views/failures_root_problem_list.xml',
        'views/failures_product.xml',
    ],
}
