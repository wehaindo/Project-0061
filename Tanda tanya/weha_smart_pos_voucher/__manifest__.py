{
    "name" : "WEHA Smart POS - POS Voucher",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale','weha_smart_pos_base_payment'],
    "author": "WEHA",
    'summary': 'Manage Customer Voucher',
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
        'views/Gift_voucher_view.xml',
        'views/pos_config_settings.xml',
        'views/pos_payment_method_view.xml',
    ],
     'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_voucher/static/src/css/voucher.css',
            'weha_smart_pos_voucher/static/src/css/style.css',
            'weha_smart_pos_voucher/static/src/js/**/*.js',
            'weha_smart_pos_voucher/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}