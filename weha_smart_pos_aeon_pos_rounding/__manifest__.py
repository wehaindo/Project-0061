{
    "name" : "WEHA Smart POS - AEON POS Rounding",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : [
        'point_of_sale',
        'weha_smart_pos_disable_refund'
    ],
    "author": "WEHA",
    'summary': 'Manage Rounding for Cash Payment',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 0,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
    ],
    'assets': { 
        'point_of_sale.assets': [
            'weha_smart_pos_aeon_pos_rounding/static/src/js/**/*.js',
            'weha_smart_pos_aeon_pos_rounding/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}