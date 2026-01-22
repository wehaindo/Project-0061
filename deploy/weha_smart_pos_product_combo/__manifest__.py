{
    "name" : "WEHA Smart POS - POS Product Combo",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale'],
    "author": "WEHA",
    'summary': 'POS Product Combo',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 5.00,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
        'security/ir.model.access.csv',
        'views/pos_combo_view.xml',
        'views/res_config_settings_view.xml',
    ],
     'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_product_combo/static/src/js/model.js',
            'weha_smart_pos_product_combo/static/src/js/Screens/ProductScreen/ProductScreen.js',
            'weha_smart_pos_product_combo/static/src/js/Popups/ProductComboSelectPopup.js',
            'weha_smart_pos_product_combo/static/src/xml/Popups/ProductComboSelectPopup.xml',
            # 'weha_smart_pos_product_combo/static/src/xml/Screens/ProductScreen/Orderline.xml',
            'weha_smart_pos_product_combo/static/src/xml/Screens/ProductScreen/ProductItem.xml',
            # 'weha_smart_pos_product_combo/static/src/js/model.js',
            #'weha_smart_pos_product_combo/static/src/xml/**/*.xml',
            

        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}