from odoo import models, fields, api
import uuid


class SmartPosConfig(models.Model):
    _name = 'smart.pos.config'

    def action_open_smart_pos(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/smartpos/pos?code={self.couch_id}',
            'target': '_blank',
        }

    
    company_id = fields.Many2one('res.company', 'Company', required=True)
    name = fields.Char('Name', size=255, required=True)
    couch_id = fields.Char('Couch ID', size=100)
    code = fields.Char('Code', size=5, required=True)

    is_pwa = fields.Boolean('Enable PWA' , default=False)
    is_offline_support = fields.Boolean('Offline Support', default=False)
    is_restaurant = fields.Boolean('Is Restaurant', default=False)
    is_picking_per_order = fields.Boolean('Picking Per Order', default=False)
    
    currency_id = fields.Integer('Currency')
    pricelist_id = fields.Integer('Pricelist')
    stock_picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type')
    smart_pos_payment_method_ids = fields.Many2many('smart.pos.payment.method', 'smart_pos_config_smart_pos_payment_method_rel', 'smart_pos_config_id', 'smart_pos_payment_method_id', 'Available Payment Methods') 
    
    show_product = fields.Boolean('Show Product', default=True)
    show_new_order = fields.Boolean('Show New Order', default=True)
    show_hold_order = fields.Boolean('Show Hold Order', default=False)
    show_note_order_line = fields.Boolean('Show Note Order Line', default=False)
    

    # id = Column(Integer, primary_key=True, autoincrement=True)
    # name = Column(String(255), nullable=False)
    # code = Column(String(5), unique=True)
    # currency_id = Column(Integer)
    # pricelist_id = Column(Integer)
    # company_id = Column(Integer, ForeignKey("company.id"), nullable=True)
    # company = relationship("Company")
    # pos_payment_methods = relationship(
    #     "PosPaymentMethod", secondary=assoc_pos_config_pos_payment_method, backref="pos_config"
    # )

    @api.model
    def create(self, vals):
        vals['couch_id'] = str(uuid.uuid4())
        return super(SmartPosConfig, self).create(vals)


    def write(self, vals):
        if not self.couch_id:
            vals['couch_id'] = str(uuid.uuid4())
        return super(SmartPosConfig, self).write(vals)