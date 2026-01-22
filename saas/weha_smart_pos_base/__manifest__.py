{
    "name" : "WEHA Smart POS - POS Base",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale'],
    "author": "WEHA",
    'summary': 'Simplify POS Layout',
    "description": """
        Purpose : WEHA - POS Retail
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
        'security/ir.model.access.csv',
        'wizards/wizard_send_message_view.xml',
        'views/res_config_settings_view.xml',
        'views/res_users_view.xml',
        'views/pos_config_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_base/static/src/css/*.css',  
            'weha_smart_pos_base/static/libs/*.js',       
            'weha_smart_pos_base/static/src/js/**/*.js',
            'weha_smart_pos_base/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}