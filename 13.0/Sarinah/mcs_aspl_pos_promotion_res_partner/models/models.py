# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    member_type = fields.Selection([('regular', 'Regular'),
                                      ('vip', 'VIP'),
                                      ('employee', 'Employee'),
                                      ], string="Member type", required=True, default='regular')