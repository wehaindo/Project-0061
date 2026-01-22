# -*- coding: utf-8 -*-
{
    'name': "Pos Receipt Barcode",

    'summary': """
      Adding barcode to pos receipt""",

    'description': """
        Adding barcode to pos receipt
    """,
    'version': '.1',
    # Author
    'author': "Kaizen Principles",
    'website': 'https://erp-software.odoo-saudi.com/discount/',
    'category': 'Point of Sale',
    'license': 'LGPL-3',

    'depends': ['base', "point_of_sale", 'web'],

    'assets': {
        'point_of_sale.assets': [
            'pos_receipt_barecode/static/src/xml/pos_reciept.xml',
            'web/static/lib/zxing-library/zxing-library.js',
            'pos_receipt_barecode/static/src/js/JsBarcode.all.min.js',
            'pos_receipt_barecode/static/src/js/pos_receipt.js',
        ],
    },

    'images': ['static/description/banner.png'],
    # Technical
    'installable': True,
    'auto_install': False,
    'price': 9.00,
    'currency': 'USD',

}
