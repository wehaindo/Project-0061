#################################################################################
# Author      : WEHA Consultant (<www.weha-id.com>)
# Copyright(c): 2015-Present WEHA Consultant.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    preparation_line_id = fields.Many2one('account.payment.preparation.line', 'Line #', ondelete='set null') 
    preparation_id = fields.Many2one('account.payment.preparation', related="preparation_line_id.preparation_id")