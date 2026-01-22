{
    "name" : "WEHA Smart POS - AEON Self Order Kiosk",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : [
        'point_of_sale',
    ],
    "author": "WEHA",
    'summary': 'Module for AEON Self Order Kiosk',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'images': ['static/description/main_background.png'],
    "data": [        
        'views/res_config_settins_view.xml',
    ],
     'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_aeon_kiosk/static/src/js/**/*.js',
            'weha_smart_pos_aeon_kiosk/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}