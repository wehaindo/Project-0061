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
    'name': 'POS Gift Voucher (Community)',
    'category': 'POS Gift Voucher',
    'summary': 'Make Vouchers and Redeem Vouchers',
    'description': """POS Gift Voucher""",
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'price': 30,
    'currency': 'EUR',
    'version': '1.0.0',
    'depends': ['base', 'point_of_sale'],
    'currency': 'EUR',
    "data": [
        'security/ir.model.access.csv',
        'views/pos_config_settings.xml',
        'views/Gift_voucher_view.xml',
        'views/pos_payment_method_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'aspl_gift_voucher/static/src/css/voucher.css',
            'aspl_gift_voucher/static/src/css/style.css',
            'aspl_gift_voucher/static/src/js/models.js',
            'aspl_gift_voucher/static/src/js/Screens/ProductScreen/ControlButtons/giftVoucherControlButton.js',
            'aspl_gift_voucher/static/src/js/Screens/GiftVoucherScreen/GiftVoucherScreen.js',
            'aspl_gift_voucher/static/src/js/Screens/GiftVoucherScreen/GiftVoucherLine.js',
            'aspl_gift_voucher/static/src/js/Screens/PaymentScreen/PaymentScreen.js',
            'aspl_gift_voucher/static/src/js/Popups/giftVoucherRedeemPopup.js',
            'aspl_gift_voucher/static/src/js/Screens/PaymentScreen/PaymentScreendisabledNumpad.js',
            'aspl_gift_voucher/static/src/xml/Screens/ProductScreen/ControlButtons/giftVoucherControlButton.xml',
            'aspl_gift_voucher/static/src/xml/Screens/GiftVoucherScreen/GiftVoucherScreen.xml',
            'aspl_gift_voucher/static/src/xml/Screens/GiftVoucherScreen/GiftVoucherLine.xml',
            'aspl_gift_voucher/static/src/xml/Screens/PaymentScreen/PaymentScreen.xml',
            'aspl_gift_voucher/static/src/xml/Popups/giftVoucherRedeemPopup.xml',
            'aspl_gift_voucher/static/src/xml/Screens/PaymentScreen/PaymentScreendisabledNumpad.xml',
        ],
    },
    'license': 'LGPL-3',
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
