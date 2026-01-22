#################################################################################
# Author      : WEHA Consultant (<www.weha-id.com>)
# Copyright(c): 2015-Present WEHA Consultant.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{
    'name': 'WEHA - Odoo Interface',
    'version': '16.0.1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'summary': 'Android Interface for Odoo POS',
    'description': """
Use common device without the IoT Box in the Point of Sale
""",
    'depends': ['point_of_sale'],
    'data': [
        # 'views/pos_config_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'assets': {
        'point_of_sale.assets': [
            'weha_odoo_interface/static/src/js/**/*',
            'weha_odoo_interface/static/src/xml/**/*',
        ],
    },
    'license': 'LGPL-3',
}