{
    "name" : "WEHA Smart POS - AEON POS Promotion",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale',
                 'weha_smart_pos_aeon_pos_data',
                 'weha_smart_pos_aeon_price',
                 #'weha_smart_pos_aeon_discount',
    ],

    "author": "WEHA",
    'summary': 'POS Promotion',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 0.00,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
        'security/ir.model.access.csv',
        'views/pos_promotion_view.xml',
        'views/pos_product_brand_view.xml',
        'views/product_template_view.xml'
    ],
    'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_aeon_promotion/static/src/js/**/*.js',
            'weha_smart_pos_aeon_promotion/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}