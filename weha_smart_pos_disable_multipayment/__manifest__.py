# -*- coding: utf-8 -*-
{
    'name': 'Weha Smart POS - Disable Multi Payment',
    'version': '16.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Restrict adding multiple payment lines with same payment method type',
    'description': """
        This module restricts users from adding multiple payment lines 
        with the same payment method type (e.g., multiple cash payments).
    """,
    'author': 'Weha',
    'website': 'https://weha.co.id',
    'depends': ['point_of_sale'],
    'data': [],
    'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_disable_multipayment/static/src/js/PaymentScreen.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}