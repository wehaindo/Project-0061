from odoo import models, fields, api, _ 
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class ProductSubCategory(models.Model):
    _inherit = "product.sub.category"

    is_member_discount = fields.Boolean('Member Discount', default=False)
    member_discount_percentage = fields.Float('Member Discount Percentage', default=0.0)
    is_member_day_discount = fields.Boolean('Member Day Discount', default=False)
    member_day_discount_percentage = fields.Float('Member Day Discount Percentage', default=0.0)
 
