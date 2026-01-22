{
    "name" : "WEHA Smart POS - AEON POS Access Rights",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale',
                 'weha_smart_pos_login',
                 'multi_branch_base'],
    "author": "WEHA",
    'summary': 'POS Access Rights',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 0,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [        
        'views/res_config_settings_view.xml',
        'views/res_branch_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_access_rights/static/src/js/**/*.js',
            'weha_smart_pos_access_rights/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}