{
    "name" : "WEHA Smart POS - POS Order Backup Restore",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale'],
    "author": "WEHA",
    'summary': 'Manage POS Order Data',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 10.00,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
        'views/res_config_settings_view.xml',
    ],
     'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_order_backup/static/src/js/**/*.js',
            'weha_smart_pos_order_backup/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}