{
    "name" : "WEHA Smart POS - POS Activity Log",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale','pos_hr'],
    "author": "WEHA",
    'summary': 'POS Auto Lock',
    "description": """
        Purpose : POS Auto Lock
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 0,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [],
    'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_aeon_auto_lock/static/src/js/**/*.js',
            'weha_smart_pos_aeon_auto_lock/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}