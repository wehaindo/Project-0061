# -*- coding: utf-8 -*-

{
    'name': 'WEHA Smart Pos - AEON Product Multi UOM',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'Azkob',
    'summary': 'Allows you to sell one products in different units of measure in Sales and POS',
    'description': "Allows you to sell one products in different units of measure in Sales and POS",
    'depends': ['sale',
                'point_of_sale',
                'multi_branch_base',
                'weha_smart_pos_aeon_pos_data',
                'weha_smart_pos_aeon_sku'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_aeon_multi_uom/static/src/js/pos.js',
            'weha_smart_pos_aeon_multi_uom/static/src/xml/**/*',
        ],
    },
    'images': [
        'static/description/popup.jpg',
    ],
    'installable': True,
    'auto_install': False,
}
