{
    "name" : "WEHA Smart POS - POS Other Popup",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale'],
    "author": "WEHA",
    'summary': 'POS Other Popup',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 0.0,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [],
    'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_popup/static/src/css/pos.scss',
            'weha_smart_pos_popup/static/src/js/**/*.js',
            'weha_smart_pos_popup/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}