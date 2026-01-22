{
    "name" : "WEHA Smart POS - AEON Payment Preparation",
    "version" : "16.0.1.0",
    "category" : "Accounting/Accounting",
    "depends" : ['account',
                'purchase',
                'multi_branch_base',
                'weha_agreement_management'],
    "author": "WEHA",
    'summary': 'Payment Preparation',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 0,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
        'security/ir.model.access.csv',
        'views/account_payment_preparation_view.xml',
    ],
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}