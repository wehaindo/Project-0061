from odoo import api, models, fields, api
from odoo.exceptions import Warning, ValidationError
import uuid
from datetime import datetime
from random import randrange

AVAILABLE_STATES = [
    ('unpaid','UnPaid'),
    ('paid', 'Paid'),
    ('posted', 'Posted'),
    ('hold', 'Hold'),
    ('cancel', 'Cancel')
]

class SmartPosOrder(models.Model):
    _name = 'smart.pos.order'
    _description = 'Smart Pos Order'
    _order = 'date_order desc'
    
    def generate_12_random_numbers(self):
        numbers = []
        for x in range(12):
            numbers.append(randrange(10))
        return numbers

    def calculate_checksum(self,ean):
        """
        Calculates the checksum for an EAN13
        @param list ean: List of 12 numbers for first part of EAN13
        :returns: The checksum for `ean`.
        :rtype: Integer
        """
        assert len(ean) == 12, "EAN must be a list of 12 numbers"
        sum_ = lambda x, y: int(x) + int(y)
        evensum = reduce(sum_, ean[::2])
        oddsum = reduce(sum_, ean[1::2])
        return (10 - ((evensum + oddsum * 3) % 10)) % 10

    def create_stock_picking(self):
        for row in self:
            picking_type_id = row.smart_pos_session_id.smart_pos_config_id.stock_picking_type_id
            vals = {
                'partner_id': row.partner_id.id if row.partner_id else False,
                'user_id': False,
                'picking_type_id': picking_type_id.id,
                'location_id': picking_type_id.default_location_src_id.id,
                'location_dest_id': picking_type_id.default_location_dest_id.id
            }

            stock_picking_id = self.env['stock.picking'].create(vals)
            if not stock_picking_id:
                raise Warning("Error picking process")
            row.stock_picking_id = stock_picking_id.id
            row.create_stock_move()


            # 'name': first_line.name,
            # 'product_uom': first_line.product_id.uom_id.id,
            # 'picking_id': self.id,
            # 'picking_type_id': self.picking_type_id.id,
            # 'product_id': first_line.product_id.id,
            # 'product_uom_qty': abs(sum(order_lines.mapped('qty'))),
            # 'state': 'draft',
            # 'location_id': self.location_id.id,
            # 'location_dest_id': self.location_dest_id.id,
            # 'company_id': self.company_id.id,

    def create_stock_move(self):
        for smart_pos_order_line_id in self.smart_pos_order_line_ids:
            move = self.env['stock.move'].create({
                #'name': 'Use on MyLocation',
                'picking_id': self.stock_picking_id.id,
                'location_id': self.stock_picking_id.location_id.id,
                'location_dest_id': self.stock_picking_id.location_dest_id.id,
                'product_id': smart_pos_order_line_id.product_id.id,
                'product_uom': smart_pos_order_line_id.product_id.uom_id.id,
                'product_uom_qty': smart_pos_order_line_id.qty,
                'state': 'draft',
            })
            move._action_confirm()
            move._action_assign()
            # This creates a stock.move.line record.
            # You could also do it manually using self.env['stock.move.line'].create({...})
            move.move_line_ids.write({'qty_done': smart_pos_order_line_id.qty}) 
            move._action_done()

    def calculate(self):
        amount_total = 0
        for smart_pos_order_line_id in self.smart_pos_order_line_ids:
            amount_total = amount_total + smart_pos_order_line_id.amount_total
        self.amount_total = amount_total
        
    name = fields.Char('Name', size=255)
    couch_id = fields.Char('Couch ID', size=100)
    barcode = fields.Char('Barcode', size=50)
    date_order = fields.Datetime('Order Date', default=datetime.now())
    smart_pos_config_id = fields.Many2one('smart.pos.config', 'Pos Config #', index=True)
    amount_paid = fields.Float('Amount Paid', default=0.0)
    amount_total = fields.Float('Amount Total', default=0.0)
    amount_tax = fields.Float('Amount Tax', default=0.0)
    amount_return = fields.Float('Amount Return', default=0.0)
    #smart_pos_session_id = fields.Many2one('smart.pos.session', 'Session #')
    partner_id = fields.Many2one('res.partner', 'Customer', index=True)
    user_id = fields.Many2one('res.users', 'User #', index=True)
    stock_picking_id = fields.Many2one('stock.picking','Picking #', readonly=True)
    smart_pos_order_line_ids = fields.One2many('smart.pos.order.line', 'smart_pos_order_id', 'Order Lines')
    smart_pos_order_payment_ids = fields.One2many('smart.pos.order.payment', 'smart_pos_order_id', 'Order Payments')
    state = fields.Selection(AVAILABLE_STATES, 'Status', default='unpaid', index=True)

    # id = Column(Integer, primary_key=True, autoincrement=True)
    # name = Column(String(255))
    # amount_paid = Column(Float)
    # amount_total = Column(Float)
    # amount_tax = Column(Float)
    # amount_return = Column(Float)
    # pos_session_id = Column(Integer, ForeignKey("pos_session.id"), nullable=True)
    # pos_session  = relationship("PosSession")
    # pricelist_id = Column(Integer)
    # partner_id = Column(Integer)
    # user_id = Column(Integer, ForeignKey("ab_user.id"), nullable=True)
    # user  = relationship("User")
    # employee_id = Column(Integer)
    # uid = Column(Integer)
    # sequence_number = Column(Integer)
    # creation_date = Column(DateTime)
    # fiscal_position_id = Column(Integer)
    # server_id = Column(Integer)
    # to_invoice = Column(Boolean)
    # state = Column(String(50), default='unpaid')

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence']
        next_code = seq.next_by_code('smart.pos.order.sequence') or '/'
        vals['name'] = next_code
        vals['couch_id'] = str(uuid.uuid4())

        # numbers = self.generate_12_random_numbers()
        # numbers.append(self.calculate_checksum(numbers))
        # vals['barcode'] = ''.join(map(str, numbers))
        
        return super(SmartPosOrder, self).create(vals)

    def write(self, vals):
        if not self.couch_id:
            vals['couch_id'] = str(uuid.uuid4())
        return super(SmartPosOrder, self).write(vals)

class SmartPosOrderLine(models.Model):
    _name = 'smart.pos.order.line'

    couch_id = fields.Char('Couch ID', size=100)
    smart_pos_order_id = fields.Many2one('smart.pos.order', 'Pos Order #')
    description = fields.Char('Description', size=250)
    product_id = fields.Many2one('product.template', 'Product')
    qty = fields.Float('Quantity', default=1.0)
    price_unit = fields.Float('Price')
    tax_id = fields.Many2one('account.tax', 'Tax')
    amount_tax = fields.Float('Amount Tax', default=0.0)
    amount_discount = fields.Float('Amount Discount', default=0.0)
    amount_total = fields.Float('Amount Total', default=0.0)
    
    @api.model
    def create(self, vals):
        vals['couch_id'] = str(uuid.uuid4())
        res =  super(SmartPosOrderLine, self).create(vals)    
        # res.smart_pos_order_id.calculate()
        return res
    


class SmartPosOrderPayment(models.Model):
    _name = 'smart.pos.order.payment'

    couch_id = fields.Char('Couch ID', size=100)
    smart_pos_order_id = fields.Many2one('smart.pos.order', 'Pos Order #')
    smart_pos_payment_method_id = fields.Many2one('smart.pos.payment.method', 'Payment Method')
    discount_in_percentage = fields.Float('Discount %', default=0.0)
    amount_discount = fields.Float('Amount Discount', default=0.0)
    amount_total = fields.Float('Amount Total', default=0.0)

    @api.model
    def create(self, vals):
        vals['couch_id'] = str(uuid.uuid4())
        res =  super(SmartPosOrderPayment, self).create(vals)    
        return res