{
    "name" : "WEHA Smart POS - AEON POS Price Check",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale'],
    "author": "WEHA",
    'summary': 'POS Price Check',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 0,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
        'views/res_config_settings_view.xml',
        'views/templates.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_aeon_price_check/static/src/js/**/*.js',
            'weha_smart_pos_aeon_price_check/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}