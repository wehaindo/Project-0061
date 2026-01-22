{
    "name" : "WEHA BCA ECR",
    "version" : "18.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale'],
    "author": "WEHA",
    'summary': 'BCA ECR Payment Integration for Odoo POS',
    "description": """BCA ECR Payment Integration for Odoo POS""",
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 0,
    'currency': 'USD',    
    "data": [],
    'assets': {
        'point_of_sale._assets_pos': [            
            'weha_smart_pos_bca_ecr/static/src/libs/BcaEcrMessageBuilder.js',
            'weha_smart_pos_bca_ecr/static/src/libs/BcaEcrMessageParser.js',
            'weha_smart_pos_bca_ecr/static/src/app/payment_bcaecr.js',
            'weha_smart_pos_bca_ecr/static/src/app/payment_bcaecr_manual.js',
            'weha_smart_pos_bca_ecr/static/src/overrides/components/payment_screen/payment_screen.js',
            # 'weha_smart_pos_bca_ecr/static/src/overrides/components/payment_screen/payment_lines/payment_lines.js',
            'weha_smart_pos_bca_ecr/static/src/overrides/components/payment_screen/payment_lines/payment_lines.xml',
            
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}