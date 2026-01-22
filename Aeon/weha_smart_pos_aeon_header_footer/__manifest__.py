{
    "name" : "WEHA Smart POS - AEON POS Header Footer",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale','multi_branch_base'],
    "author": "WEHA",
    'summary': 'POS Header Footer per Store',
    "description": """
        Purpose : POS Header Footer per Store
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 0,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
        'views/res_config_settings_view.xml',
        'views/res_branch_view.xml'
    ],
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}