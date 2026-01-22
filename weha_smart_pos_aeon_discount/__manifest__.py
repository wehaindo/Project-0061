{
    "name" : "WEHA Smart POS - AEON Discount",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : [
        'point_of_sale',
        'multi_branch_base',
        'weha_smart_pos_aeon_pos_data',
        'weha_smart_pos_aeon_pms',
        'weha_smart_pos_aeon_price',
        'weha_smart_pos_aeon_promotion',
        'weha_smart_pos_aeon_sku',
        'weha_smart_pos_aeon_multi_uom',
    ],
    "author": "WEHA",
    'summary': 'Module for AEON PMS',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'images': ['static/description/main_background.png'],
    "data": [        
        #'security/ir.model.access.csv',
        # 'views/product_product_view.xml',
        'views/product_category_view.xml',
        'views/product_subcategory_view.xml',
        # 'views/pos_order_view.xml',
    ],
     'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_aeon_discount/static/src/js/**/*.js',
            'weha_smart_pos_aeon_discount/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}