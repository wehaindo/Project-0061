{
    'name': 'POS Foodcourt',
    'version': '16.0.1.0',
    'description': 'POS Foodcourt',
    'summary': 'POS Foodcourt',
    'author': 'WEHA',
    'website': 'https://www.weha-id.com',
    'license': 'LGPL-3',
    'category': 'Point of sale',
    'depends': [
        'point_of_sale',
        'pos_loyalty'
    ],
    'data': [],
    'demo': [],
    'auto_install': False,
    'application': False,
    'assets': {
        'point_of_sale.assets': [
            'weha_pos_foodcourt/static/src/js/ControlButtons/eWalletButton.js',
        ],
    }
}