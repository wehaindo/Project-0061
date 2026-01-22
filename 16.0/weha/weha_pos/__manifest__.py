{
    'name': 'WEHA POS',
    'version': '16.0.1.0',
    'description': 'WEHA POS',
    'summary': 'WEHA POS',
    'author': 'WEHA',
    'website': 'https://www.weha-id.com',
    'license': 'LGPL-3',
    'category': 'Point of Sale',
    'depends': [
        'base', 
        'product',         
        'account',
        'hr', 
        'stock',         
        'weha_api'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/weha_pos_order_menu.xml',
        'views/weha_pos_order_views.xml'
    ],
    'demo': [
        ''
    ],
    'auto_install': False,
    'application': False,
    'assets': {
        
    }
}