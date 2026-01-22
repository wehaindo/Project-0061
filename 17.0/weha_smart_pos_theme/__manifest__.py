{
    "name" : "WEHA Smart POS - POS Theme",
    "version" : "17.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale'],
    "author": "WEHA",
    'summary': 'Improve Several Features for Point of Sale',
    "description": """
        Purpose : Improve more features for Point of sale 
        Feature : Customize POS Theme Layout                  
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 0.00,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [ ],
    'assets': {
        'point_of_sale._assets_pos': [
            'weha_smart_pos_theme/static/src/**/*',            
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}