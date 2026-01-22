{
    "name" : "WEHA Smart POS - POS Interface",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale'],
    "author": "WEHA",
    'summary': 'POS local hardware interface',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'images': ['static/description/main_background.png'],
    "data": [
        # 'views/pos_payment_method_view.xml',
    ],
     'assets': {
        'point_of_sale.assets': [
            # 'weha_smart_pos_aeon_interface/static/lib/aeon_interface.js',
            'weha_smart_pos_aeon_interface/static/lib/websocket_client.js',
            'weha_smart_pos_aeon_interface/static/src/js/**/*.js',
            'weha_smart_pos_aeon_interface/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}