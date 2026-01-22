# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Purchase Approval',
    'category': 'WEHA',
    'summary': 'Purchase Approval',
    'description': """
This module Purchase Approval.
""",
    'depends': ['base', 'mail','purchase'],
    'data': [
        'security/purchase_security.xml',
        'security/ir.model.access.csv',
        'views/inherit_purchase_order_view.xml',
        'views/purchase_approval_rule_view.xml',
    ],
    'application': True,
    'license': 'LGPL-3'
   
}