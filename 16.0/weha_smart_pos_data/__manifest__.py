{
    "name" : "WEHA Smart POS - AEON POS Data",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale',
                 'multi_branch_base',
                 'multi_branch_pos',
                 'weha_smart_pos_multi_branch',
                 'weha_smart_pos_aeon_pos_data_base'
    ],
    "author": "WEHA",
    'summary': 'Speed Up POS Data Load',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 45.00,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
        # 'views/product_product_view.xml',
        # 'security/ir.model.access.csv',
        # 'views/pos_data_menu.xml',        
        # 'data/ir_cron_data.xml',
        'views/res_config_settings_view.xml',
        # 'views/product_category_view.xml',
        'views/product_pricelist_view.xml',
        'views/res_branch_view.xml',
        'views/pos_session_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_data/static/lib/**/*.js',
            'weha_smart_pos_data/static/src/js/**/*.js',
            'weha_smart_pos_data/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}