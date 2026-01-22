{
    "name" : "WEHA Smart POS - AEON PRIMA",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['base',
                 'point_of_sale',
                 'payment',
                 'weha_smart_pos_aeon_bca_ecr',
                 'weha_smart_pos_disable_refund',
                 'weha_smart_pos_aeon_customer_display',                 
                ],
    "author": "WEHA",
    'summary': 'Integration QRIS Payment with DSP (PRIMA)',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 0,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
        'security/ir.model.access.csv',
        'views/res_config_settings_view.xml',
        'wizards/wizard_prima_session_report.xml',
        'views/pos_session_view.xml',
        'views/prima_session_report.xml'
        # 'views/pos_payment_method_view.xml',
        # 'views/pos_order_view.xml'
    ],
    'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_aeon_prima/static/src/js/**/*.js',
            'weha_smart_pos_aeon_prima/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}