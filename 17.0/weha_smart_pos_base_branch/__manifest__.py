{
    "name" : "WEHA Smart POS - POS Branch",
    "version" : "17.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale','weha_smart_pos_base'],
    "author": "WEHA",
    'summary': 'Multi Store Support',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 85.00,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
        'security/ir.model.access.csv',
        'wizards/wizard_send_message_view.xml',
        'views/direct_login_templates.xml',
        'views/pos_config_view.xml',
        'views/res_config_settings_view.xml',
        'views/res_branch_views.xml',
        'views/branch_res_users_views.xml',
        'views/pos_session_views.xml',
        'views/pos_orders_views.xml',
        'views/product_views.xml',
        'views/discuss_channel_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'weha_smart_pos_base/static/src/**/*',
            'weha_smart_pos_base/static/src/**/*',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}