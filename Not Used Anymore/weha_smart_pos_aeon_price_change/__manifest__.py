{
    "name" : "WEHA Smart POS - AEON POS Product Price Change",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale','multi_branch_base'],
    "author": "WEHA",
    'summary': 'Speed Up POS Data Load',
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
        'views/product_price_menu.xml',
        'views/product_pricelist_view.xml',
        'views/product_price_change_view.xml',
        'views/product_product_view.xml',
    ],
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}