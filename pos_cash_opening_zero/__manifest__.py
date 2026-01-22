# -*- coding: utf-8 -*-
{
    "name": "POS Zero Default Cash Opening",
    "version": "0.0.1",
    "category": "Sales/Point of Sale",
    'summary': "Default POS cash opening value to zero, but allow modification",
    "author": "Ewetoye Ibrahim",
    "website": "https://github.com/EwetoyeIbrahim/pos_cash_opening_zero",
    "auto_install": False,
    "depends": [
        "point_of_sale",
        "pos_hr",
        "weha_smart_pos_login",
        "weha_smart_pos_aeon_pos_access_rights",
        "weha_smart_pos_aeon_activity_log",
    ],
    'installable': True,
    'application': False,
    'data': [
        'security/ir.model.access.csv',
        'views/pos_cash_count_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_cash_opening_zero/static/src/css/**/*.css',
            'pos_cash_opening_zero/static/src/js/**/*.js',
            'pos_cash_opening_zero/static/src/xml/**/*.xml',
        ]
    },
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
}
