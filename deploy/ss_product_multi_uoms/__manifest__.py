# -*- coding: utf-8 -*-

{
    'name': 'Product Multi UOM',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'Azkob',
    'summary': 'Allows you to sell one products in different units of measure in Sales and POS',
    'description': "Allows you to sell one products in different units of measure in Sales and POS",
    'depends': ['sale','point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'ss_product_multi_uoms/static/src/js/pos.js',
            'ss_product_multi_uoms/static/src/xml/**/*',
        ],
    },
    'images': [
        'static/description/popup.jpg',
    ],
    'installable': True,
    'website': 'https://azkob.com',
    'auto_install': False,
    'price': 70,
    'currency': 'EUR',
}
