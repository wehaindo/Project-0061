{
    "name" : "WEHA Smart POS - AEON PMS",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale',
                 'multi_branch_base',
                 'weha_smart_pos_disable_refund'],
    "author": "WEHA",
    'summary': 'Module for AEON PMS',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'images': ['static/description/main_background.png'],
    "data": [        
        'security/ir.model.access.csv', 
        'views/pos_order_view.xml',
        'views/pos_payment_method_view.xml',
        'views/res_config_settings_view.xml'
    ],
     'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_aeon_pms/static/src/js/**/*.js',
            'weha_smart_pos_aeon_pms/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}