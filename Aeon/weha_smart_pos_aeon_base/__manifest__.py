{
    "name" : "WEHA Smart POS - AEON POS Base",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale',
                 'multi_branch_base'
    ],
    "author": "WEHA",
    'summary': 'Module for AEON POS Base',
    "description": """
        Purpose : POS Base
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'images': ['static/description/main_background.png'],
    "data": [        
    ],
     'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_aeon_base/static/src/js/**/*.js',
            'weha_smart_pos_aeon_base/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}