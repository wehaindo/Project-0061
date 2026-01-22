{
    "name" : "WEHA Smart POS - POS Default Customer",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['base','point_of_sale'],
    "author": "WEHA",
    'summary': 'Set Default Customer for POS Order',
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
    ],
     'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_default_customer/static/src/js/**/*.js',
            'weha_smart_pos_default_customer/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}