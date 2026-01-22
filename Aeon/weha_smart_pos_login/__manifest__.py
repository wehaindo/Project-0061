{
    "name" : "WEHA Smart POS - POS Login",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale'],
    "author": "WEHA",
    'summary': 'Another POS Login',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 15.00,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
        'security/ir.model.access.csv',
        'wizards/wizard_pos_rfid_view.xml',
        'views/res_users_view.xml',
        'views/pos_config_view.xml',
        'views/templates.xml',
    ],
     'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_login/static/src/js/**/*.js',
            'weha_smart_pos_login/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}