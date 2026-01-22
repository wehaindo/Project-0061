{
    "name" : "WEHA Smart POS - POS Rest",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale','pos_restaurant','weha_smart_pos_base'],
    "author": "WEHA",
    'summary': 'POS Restaurant',
    "description": """
        Purpose : WEHA - POS Restaurant
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
    ],
    'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_rest/static/src/css/*.css',  
            'weha_smart_pos_rest/static/libs/*.js',       
            'weha_smart_pos_rest/static/src/js/**/*.js',
            'weha_smart_pos_rest/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}