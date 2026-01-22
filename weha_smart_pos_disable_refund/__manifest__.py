{
    "name" : "WEHA Smart POS - POS Disable Refund Button",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : [
        'point_of_sale',
        'pos_hr',
        'weha_smart_pos_aeon_activity_log',
        'weha_smart_pos_aeon_pos_access_rights',
    ],
    "author": "WEHA",
    'summary': 'Show or Hide Refund Control Button',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 5.00,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
        'views/res_config_settings_view.xml'
    ],
     'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_disable_refund/static/src/js/**/*.js',
            'weha_smart_pos_disable_refund/static/src/css/**/*.css',
            'weha_smart_pos_disable_refund/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}