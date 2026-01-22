{
    "name" : "WEHA Smart POS - POS Receipt Barcode",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale',
                 'weha_smart_pos_receipt_logo'],
    "author": "WEHA",
    'summary': 'POS Receipt Barcode',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 5.00,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
    ],
     'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_receipt_barcode/static/src/libs/JsBarcode.all.min.js',
            'weha_smart_pos_receipt_barcode/static/src/js/**/*.js',
            'weha_smart_pos_receipt_barcode/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}