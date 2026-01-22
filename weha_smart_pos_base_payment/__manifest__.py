{
    "name" : "WEHA Smart POS - POS Paymet Method Layout",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale','weha_smart_pos_base'],
    "author": "WEHA",
    'summary': 'Change Payment method Layout',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 5.00,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
        'views/res_config_settings_view.xml',
        'views/pos_payment_method.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_base_payment/static/src/js/**/*.js',
            'weha_smart_pos_base_payment/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}