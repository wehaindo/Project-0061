# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{
    'name': 'POS Customer Wallet',
    'category': 'Point of Sale',
    'summary': 'This module allows user to add, change to the wallet, redeem it and print Wallet Ledger.',
    'description': """
This module allows user to add, change to the wallet, redeem it and print Wallet Ledger.
""",
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'price': 19.00,
    'currency': 'EUR',
    'version': '1.0',
    'depends': ['base', 'point_of_sale'],
    'images': ['static/description/main_screenshot.png'],
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