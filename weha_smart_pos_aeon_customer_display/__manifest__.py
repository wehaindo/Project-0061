{
    "name" : "WEHA Smart POS - AEON Customer Display",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : [
        'point_of_sale',
        'multi_branch_base',
        'weha_smart_pos_aeon_price',
        'weha_smart_pos_aeon_promotion',
        'weha_smart_pos_aeon_discount',
        'total_quantity_pos'
    ],
    "author": "WEHA",
    'summary': 'Module for AEON Point of Sale',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'images': ['static/description/main_background.png'],
    "data": [
        'security/ir.model.access.csv',
        'views/res_branch_view.xml',
        'views/res_config_settings_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_aeon_customer_display/static/src/js/chrome.js',
            'weha_smart_pos_aeon_customer_display/static/src/js/ChromeWidgets/CustomerFacingDisplayButton.js',
            'weha_smart_pos_aeon_customer_display/static/src/js/ChromeWidgets/PosEnableDisplayButton.js',
            # 'weha_smart_pos_aeon_customer_display/static/src/js/**/*.js',
            'weha_smart_pos_aeon_customer_display/static/src/js/models.js',
            'weha_smart_pos_aeon_customer_display/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}