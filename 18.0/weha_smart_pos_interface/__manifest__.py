{
    'name': 'WEHA - Smart POS Interface',
    'version': '18.0.1.0',
    'description': 'Smart POS Interface',
    'summary': 'Interfacing to external resources',
    'author': 'WEHA',
    'website': 'https://www.weha-id.com',
    'license': 'LGPL-3',
    'category': 'Point of Sale',
    'depends': [
        'point_of_sale'
    ],
    'data': [],
    'demo': [
        ''
    ],
    'auto_install': False,
    'application': False,
    'assets': {
        'point_of_sale._assets_pos': [
            'weha_smart_pos_interface/static/src/js/localdatabase.js',
            'weha_smart_pos_interface/static/src/js/localreceipt.js',
        ],
    },
}