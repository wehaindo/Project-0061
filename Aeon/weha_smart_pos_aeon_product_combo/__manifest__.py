{
    "name" : "WEHA Smart POS - AEON POS Product Combo",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale'],
    "author": "WEHA",
    'summary': 'Product Combo',
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
		'views/custom_pos_view.xml',
	],
	'assets': {
		'point_of_sale.assets': [
			"weha_smart_pos_aeon_product_combo/static/src/css/custom.css",
			"weha_smart_pos_aeon_product_combo/static/src/js/bi_pos_combo.js",
            "weha_smart_pos_aeon_product_combo/static/src/js/ProductCategoriesWidget.js",
            "weha_smart_pos_aeon_product_combo/static/src/js/BiProductScreen.js",
            "weha_smart_pos_aeon_product_combo/static/src/js/PartnerScreenExtend.js",
            "weha_smart_pos_aeon_product_combo/static/src/js/SelectComboProductPopupWidget.js",
            "weha_smart_pos_aeon_product_combo/static/src/js/OrderWidgetExtended.js",
            "weha_smart_pos_aeon_product_combo/static/src/js/ProductListWidget.js",
            'weha_smart_pos_aeon_product_combo/static/src/xml/bi_pos_combo.xml',
		],
	},
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}