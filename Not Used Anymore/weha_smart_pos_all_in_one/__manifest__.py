{
    "name" : "WEHA - POS All In One",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale'],
    "author": "WEHA",
    'summary': 'POS All In One',
    "description": """
        Purpose : POS Enhancement
    """,
    "website" : "https://www.weha-id.com",
    "currency": "IDR",
    "data": [
        # 'security/ir.model.access.csv',
        # 'views/pos_assets.xml',
        # 'views/pos_menu.xml',
        # 'views/pos_promotion.xml',
        # 'views/pos_loyalty.xml',
    ],
     'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_all_in_one/static/src/css/screen.css',
            'weha_smart_pos_all_in_one/static/src/xml/Screens/ProductScreen/ProductScreen.xml',
        ],
    },
    "auto_install": False,
    "installable": True,

}