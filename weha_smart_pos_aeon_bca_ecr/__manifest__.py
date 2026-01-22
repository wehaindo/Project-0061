{
    "name" : "WEHA Smart POS - AEON BCA ECR",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['base',
                 'point_of_sale',
                 'payment'
                ],
    "author": "WEHA",
    'summary': 'BCA ECR',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 0,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
        'views/pos_payment_method_view.xml',
        'views/pos_order_view.xml'
    ],
    'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_aeon_bca_ecr/static/src/js/models.js',
            'weha_smart_pos_aeon_bca_ecr/static/src/js/payment_bca_ecr.js',
            'weha_smart_pos_aeon_bca_ecr/static/src/js/payment_bank_manual.js',            
            'weha_smart_pos_aeon_bca_ecr/static/src/js/qris_bank_manual.js',            
            'weha_smart_pos_aeon_bca_ecr/static/src/js/Screens/PaymentScreen/PaymentScreen.js',
            'weha_smart_pos_aeon_bca_ecr/static/src/js/bca_ecr_popup.js',
            'weha_smart_pos_aeon_bca_ecr/static/src/js/Popups/BankManualPopup.js',
            'weha_smart_pos_aeon_bca_ecr/static/src/js/Popups/QrisManualPopup.js',
            'weha_smart_pos_aeon_bca_ecr/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}