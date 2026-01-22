{
    "name" : "WEHA Smart POS - POS Activity Log",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale','pos_hr'],
    "author": "WEHA",
    'summary': 'POS Activity Log',
    "description": """
        Purpose : POS Activity Log
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 0,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
        'security/ir.model.access.csv',
        'views/pos_activity_log_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_aeon_activity_log/static/src/js/**/*.js',
            'weha_smart_pos_aeon_activity_log/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}