# -*- coding: utf-8 -*-
{
    'name': "DMI : Fix Promotion",

    'summary': """
        Fix Promotion
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Digloma",
    'website': "http://www.digloma.com",

    'category': 'Point of Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'mcs_aspl_pos_promotion',
        'sh_pos_receipt_extend',
        "point_of_sale",
        'srn_pos_discount_with_product',
        'sh_pos_order_return_exchange',
        'srn_pos_referral2',
        'srn_pos_referral',
        'mcs_pos_loyalty',
        'bi_product_brand',
        'yyt_custom_report',
        'pos_gift_voucher',
        'aspl_pos_promotion'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/ir.model.access.csv',
        'views/pos_promotion.xml',
        'views/product_brand.xml',
        'views/yyt_pos_order_line.xml',
        'views/pos_receipt2.xml',
        'views/pos_product_discount.xml',
        'views/payment_method.xml',
        'data/pos_promotion_cron.xml',
        'data/server_action.xml',
    ],

    "qweb": ["static/src/xml/pos.xml"],
}
