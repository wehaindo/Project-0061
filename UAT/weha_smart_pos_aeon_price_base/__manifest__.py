{
    "name" : "WEHA Smart POS - AEON POS Price Base",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale'],
    "author": "WEHA",
    'summary': 'AEON Price Base',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 0,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [],
    'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_aeon_price_base/static/src/js/**/*.js',
            'weha_smart_pos_aeon_price_base/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}