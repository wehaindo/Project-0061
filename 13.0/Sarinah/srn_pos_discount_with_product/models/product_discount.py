from odoo import api, fields, models, tools
from string import ascii_letters, digits
from odoo.exceptions import ValidationError


class ProductDiscount(models.Model):
    _name = "srn.pos.product.discount"
    _description = "list product for discount on total"

    sku = fields.Char(string="SKU", required=True, help="SKU must cointain word DCDWP")
    name = fields.Char(string="Name", required=True)
    disc_percentage = fields.Integer(string="Discount (%)", required=True, help="Less than 1 will be treat as no discount. if max_discount is filled and subtotal more than max_discount, than the discount amount will be max_discount amount.")
    max_discount = fields.Integer(string="Maximum Discount (Rp)", required=True, help="Zero for unlimited")
    only_normal_price = fields.Boolean(string="Only Normal Price", help="Applies discount for product that doesn't contains discount or promotional")
    minimum_transaction = fields.Integer(string="Minimum Transaction (Rp)", help="Zero for no minimum amount of transaction")
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active", default=True)

    _sql_constraints = [('sku_unique', 'unique(sku)', 'Product code must be unique'), ]

    @api.constrains('sku')
    def check_code(self):
        if ' ' in str(self.sku) or set(self.sku).difference(ascii_letters + digits):
            raise ValidationError("SKU tidak boleh ada spasi atau simbol")
