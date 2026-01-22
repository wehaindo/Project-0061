{
    "name" : "WEHA Smart POS - POS Api",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['base','point_of_sale'],
    "author": "WEHA",
    'summary': 'Use for WEHA Mobile POS',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 60.00,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
        'data/ir_config_param.xml',
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