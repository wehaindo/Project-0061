{
    "name" : "WEHA Smart POS - POS Product Multiple Barcode",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale','multi_branch_base'],
    "author": "WEHA",
    'summary': 'Product with multiple barcode',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'images': ['static/description/main_background.png'],
    "data": [
        'security/ir.model.access.csv',
        'views/res_config_settings_view.xml',
        'views/product_template_view.xml',
    ],
     'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_bag_charge/static/src/js/**/*.js',
            'weha_smart_pos_bag_charge/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}