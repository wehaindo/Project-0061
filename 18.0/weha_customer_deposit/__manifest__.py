{
    "name" : "WEHA Customer Deposit",
    "version" : "18.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale'],
    "author": "WEHA",
    'summary': 'POS Food Court',
    "description": """
        Purpose : WEHA Customer Deposit
        Features: 
         - Support Sale
         - Support Point of Sale
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 0,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
        'security/ir.model.access.csv',
        'data/customer_deposit_sequence.xml',
        'wizards/account_payment_register_view.xml',
        'views/customer_deposit_menu.xml',
        'views/customer_deposit_view.xml',
        'views/res_partner_view.xml',
        'views/account_journal_view.xml',
        'views/res_config_settings_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'weha_customer_deposit/static/src/app/payment_deposit.js',
            'weha_customer_deposit/static/src/components/payment_screen/payment_screen.js',
            'weha_customer_deposit/static/src/overrides/models.js',
            'weha_customer_deposit/static/src/overrides/models/pos_order.js',
            'weha_customer_deposit/static/src/components/product_screen/control_buttons/control_buttons.js',
            'weha_customer_deposit/static/src/components/product_screen/control_buttons/control_buttons.xml'
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}