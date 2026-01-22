{
    "name" : "WEHA Smart POS - POS Product Member Price",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale'],
    "author": "WEHA",
    'summary': 'Define Product Member Price',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 10.00,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
        'security/ir.model.access.csv',
        'wizards/wizard_send_message_view.xml',
        'views/point_of_sale_dashboard_view.xml',
    ],
     'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_send_message/static/src/js/**/*.js',
            'weha_smart_pos_send_message/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}