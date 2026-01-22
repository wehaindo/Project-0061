{
    'name': 'WEHA - Smart POS Aeon POS Order Log',
    'version': '16.0.1.0',
    'description': 'Smart POS Aeon POS Order Log',
    'summary': 'Smart POS Aeon POS Order Log',
    'author': 'WEHA',
    'website': 'https://www.weha-id.com',
    'license': 'LGPL-3',
    'category': 'Point of Sale',
    'depends': [
        'point_of_sale',
        'weha_smart_pos_aeon_decentralize_api',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_decentralize_view.xml',
    ],    
    'auto_install': False,
    'application': False,
    'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_aeon_pos_order_log/static/src/js/pos_order_log.js',            
            'weha_smart_pos_aeon_pos_order_log/static/src/js/pos_order_receipt_log.js',            
            'weha_smart_pos_aeon_pos_order_log/static/src/js/Screens/PaymentScreen/PaymentScreen.js',
            'weha_smart_pos_aeon_pos_order_log/static/src/js/Screens/ReceiptScreen/RecieptScreen.js',                        
        ],
    }
}