{
    "name" : "WEHA Smart POS - POS Food Court",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale', 'weha_smart_pos_base'],
    "author": "WEHA",
    'summary': 'POS Food Court',
    "description": """
        Purpose : WEHA - POS Food Court
        Features: 
         - Order
         - Hold Order
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 0,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
        'security/ir.model.access.csv',
    ],
    'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_foodcourt/static/src/css/*.css',  
            'weha_smart_pos_foodcourt/static/src/js/**/*.js',
            'weha_smart_pos_foodcourt/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}