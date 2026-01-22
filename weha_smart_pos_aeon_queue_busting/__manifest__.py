{
    "name" : "WEHA Smart POS - AEON Queue Busting",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale'],
    "author": "WEHA",
    'summary': 'POS Queue Busting',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 0.00,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [],
    'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_aeon_queue_busting/static/src/js/Screens/ProductScreen/ProductScreen.js',            
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}