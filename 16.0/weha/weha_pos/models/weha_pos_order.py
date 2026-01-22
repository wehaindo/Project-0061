from odoo import models, fields, api
import uuid

class WehaPosConfig(models.Model):
    _name = 'weha.pos.config'
    
    server_id = fields.Char('UUID')
    name = fields.Char('Name')                   
    
    @api.model
    def create(self, vals):
        vals['server_id'] = str(uuid.uuid4())
        res = super(WehaPosConfig, self).create(vals)
        return res 
    
class WehaPosOrder(models.Model):
    _name = 'weha.pos.order'
    _description = 'WEHA POS Order'

    server_id = fields.Char('UUID')
    name = fields.Char(
        string='Order Reference', 
        required=True, 
        copy=False, 
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('weha.pos.order')
    )    
    date_order = fields.Datetime('Order Date')
    customer_id = fields.Many2one('res.partner', string='Customer')
    order_line_ids = fields.One2many('weha.pos.order.line', 'order_id', string='Order Lines')
    payment_ids = fields.One2many('weha.pos.order.payment', 'order_id', string='Payments')
    amount_total = fields.Float(string='Total')
    amount_paid = fields.Float(string='Paid')
    amount_tax = fields.Float(string='Tax')
    state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid')
    ], string='Status')
    
    @api.depends('order_line_ids.subtotal')
    def _compute_total(self):
        for order in self:
            order.total = sum(line.subtotal for line in order.order_line_ids)

    @api.depends('payment_ids.amount')
    def _compute_amount_paid(self):
        for order in self:
            order.amount_paid = sum(p.amount for p in order.payment_ids)

    @api.depends('amount_paid', 'total')
    def _compute_payment_status(self):
        for order in self:
            if order.amount_paid >= order.total:
                order.payment_status = 'paid'
            elif order.amount_paid > 0:
                order.payment_status = 'partial'
            else:
                order.payment_status = 'not_paid'

class WehaPosOrderLine(models.Model):
    _name = 'weha.pos.order.line'
    _description = 'WEHA POS Order Line'

    server_id = fields.Char('UUID')
    order_id = fields.Many2one('weha.pos.order', string='Order')
    product_id = fields.Many2one('product.product', string='Variant Product')
    product_template_id = fields.Many2one('product.template', string='Product Template', compute='_compute_product_template', store=True)
    product_attributes = fields.Char(string='Variant Attributes', compute='_compute_product_attributes', store=True)
    quantity = fields.Integer(string='Quantity', default=1)
    price_unit = fields.Float(string='Unit Price')
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    
    @api.depends('product_id')
    def _compute_product_template(self):
        for line in self:
            line.product_template_id = line.product_id.product_tmpl_id

    @api.depends('product_id')
    def _compute_product_attributes(self):
        for line in self:
            if line.product_id and line.product_id.attribute_value_ids:
                line.product_attributes = ', '.join(val.name for val in line.product_id.attribute_value_ids)
            else:
                line.product_attributes = ''

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit

class WehaPosOrderPayment(models.Model):
    _name = 'weha.pos.order.payment'
    _description = 'WEHA POS Order Payment'

    server_id = fields.Char('UUID')
    order_id = fields.Many2one('weha.pos.o.order', string='Order', required=True)
    payment_date = fields.Datetime(string='Payment Date', default=fields.Datetime.now)
    payment_method_id = fields.Many2one('weha.pos.payment.method','Pos Payment Method', required=True)
    amount = fields.Float(string='Amount', required=True)

class WehaPosPaymentMethod(models.Model):
    _name = 'weha.pos.payment.method'
    
    server_id = fields.Char('UUID')
    name = fields.Char('Name')
    is_cash = fields.Boolean('Is Cash')
    is_rouded = fields.Boolean('Is Rounded')
    is_voucher = fields.Boolean('Is Voucher')
    
    @api.model
    def create(self, vals):
        vals['server_id'] = str(uuid.uuid4())
        res = super(WehaPosPaymentMethod, self).create(vals)
        return res 
    
class WehaPosProductCategory(models.Model):
    _name = 'weha.pos.product.category'
    
    server_id = fields.Char('UUID')
    name = fields.Char("Pos Product Category")

    @api.model
    def create(self, vals):
        vals['server_id'] = str(uuid.uuid4())
        res = super(WehaPosProductCategory, self).create(vals)
        return res 
    
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    server_id = fields.Char('UUID')
    pos_product_category_id = fields.Many2one('weha.pos.product.category', 'Pos Product Category')    
    
    
    @api.model
    def create(self, vals):
        vals['server_id'] = str(uuid.uuid4())
        res = super(ProductTemplate, self).create(vals)
        return res 