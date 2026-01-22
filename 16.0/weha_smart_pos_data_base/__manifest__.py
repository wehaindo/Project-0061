{
    "name" : "WEHA Smart POS - POS Data Base",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : [
        'point_of_sale',        
        'multi_branch_base',
        'multi_branch_pos',        
        'weha_smart_pos_multi_branch'
    ],
    "author": "WEHA",
    'summary': 'Base for POS Data',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 0,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
        'security/ir.model.access.csv',
        'views/product_product_view.xml',
        'views/res_branch_view.xml',
        'views/product_pricelist_view.xml',
        'views/res_config_settings_view.xml'
    ],
    'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_data_base/static/lib/**/*.js',
            'weha_smart_pos_data_base/static/src/js/**/*.js',
            'weha_smart_pos_data_base/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}