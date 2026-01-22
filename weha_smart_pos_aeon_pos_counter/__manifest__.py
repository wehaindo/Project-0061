{
    "name" : "WEHA Smart POS - AEON POS Counter",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale'],
    "author": "WEHA",
    'summary': 'POS Counter',
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
        'views/product_product_view.xml',
    ],
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}