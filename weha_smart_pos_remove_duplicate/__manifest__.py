# -*- coding: utf-8 -*-
{
    'name': 'Weha Smart POS - Remove Duplicate Order Lines',
    'version': '16.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Remove duplicate POS order lines by session',
    'description': """
        This module provides functionality to detect and remove duplicate 
        POS order lines. Access via wizard to scan, review, and remove duplicates.
    """,
    'author': 'Weha',
    'website': 'https://www.weha-id.com',
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/remove_duplicate_wizard_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
