{
    "name" : "WEHA Smart POS - AEON POS Delete Order Line",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : [
        'point_of_sale',
        'weha_smart_pos_aeon_pos_access_rights',
        'weha_smart_pos_aeon_activity_log',
    ],
    "author": "WEHA",
    'summary': 'Delete POS Order Line',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 0,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
    ],
    'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_aeon_pos_order_line/static/src/js/models.js',
            'weha_smart_pos_aeon_pos_order_line/static/src/js/clear_button.js',
            'weha_smart_pos_aeon_pos_order_line/static/src/js/clear_order_line.js',
            # 'weha_smart_pos_aeon_pos_order_line/static/src/js/change_qty.js',
            'weha_smart_pos_aeon_pos_order_line/static/src/xml/clear_button.xml',
            'weha_smart_pos_aeon_pos_order_line/static/src/xml/clear_order_line.xml',
            # 'weha_smart_pos_aeon_pos_order_line/static/src/xml/change_qty.xml'
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}