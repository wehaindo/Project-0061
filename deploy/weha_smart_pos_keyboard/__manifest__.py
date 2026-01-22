{
    "name" : "WEHA Smart POS - POS Keyboard (Windows OSK Keyboard)",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale'],
    "author": "WEHA",
    'summary': 'OnScreen Keyboard using Windows OSK Keyboard',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 5.00,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [],
     'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_keyboard/static/src/css/kioskboard-2.3.0.min.css',
            'weha_smart_pos_keyboard/static/src/libs/kioskboard.js',
            'weha_smart_pos_keyboard/static/src/js/**/*.js',
            'weha_smart_pos_keyboard/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}