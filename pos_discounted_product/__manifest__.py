# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
    "name":  "POS Show Discounted Price",
    "summary":  """Now show discounted price along with base price of the products on point of sale.Discounted Product|Custom Discounted Product|Show Discounted Product|Discounted Price""",
    "category":  "Point Of Sale",
    "version":  "1.1",
    "sequence":  1,
    "author":  "Webkul Software Pvt. Ltd.",
    "license":  "Other proprietary",
    "website":  "https://store.webkul.com/OpenERP-POS-Discounted-Products.html",
    "description":  """http://webkul.com/blog/odoo-pos-show-discounted-price-2/""",
    "live_test_url":  "http://odoodemo.webkul.com/?module=pos_discounted_product&custom_url=/pos/auto",
    "depends":  [
        'point_of_sale',
        'sale',
    ],
    "demo":  ['data/pos_discounted_product_demo.xml'],
    "assets": {

        'point_of_sale.assets':
        ['pos_discounted_product/static/src/js/main.js',
         'pos_discounted_product/static/src/xml/**/*',
         ],
    },
    "images":  ['static/description/Banner.png'],
    "application":  True,
    "installable":  True,
    "auto_install":  False,
    "price":  20,
    "currency":  "USD",
    "pre_init_hook":  "pre_init_check",
}
