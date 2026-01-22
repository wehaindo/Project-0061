# -*- coding: utf-8 -*-
{
    'name': 'POS Customer Coupon',
    'category': 'Point of Sale',
    'summary': 'POS Customer Coupon',
    'description': """""",
    'author': 'WEHA Consultant',
    'website': 'https://www.weha-id.com',
    'price': 0,
    'currency': 'IDR',
    'version': '14.0.1.0',
    'depends': ['base', 'point_of_sale'],
    'images': [],
    "data": [
        'security/ir.model.access.csv',
        'views/point_of_sale.xml',
        'views/aspl_pos_wallet.xml',
        'views/wallet_management_view.xml',
    ],
    'qweb': [
        'static/src/xml/ControlButtons/PrintWalletLedger.xml',
        'static/src/xml/ControlButtons/AddToWallet.xml',
        'static/src/xml/Popups/AddMoneyToWallet.xml',
        'static/src/xml/Popups/PaymentWallet.xml',
        'static/src/xml/Popups/PrintLedger.xml',
        'static/src/xml/Screens/ClientListScreen.xml',
        'static/src/xml/Screens/PaymentScreen.xml',
        'static/src/xml/Screens/WalletHistoryScreen.xml',
        'static/src/xml/Screens/WalletHistoryList.xml',
        'static/src/xml/Screens/ReceiptScreen.xml',
        'static/src/xml/Screens/WalletLedgerReceipt.xml',
        'static/src/xml/Screens/OrderReceipt.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: