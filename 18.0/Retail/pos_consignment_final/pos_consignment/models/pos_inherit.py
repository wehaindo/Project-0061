
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = "product.product"

    is_consignment = fields.Boolean(string='Is Consignment', compute='_compute_is_consignment', store=False)

    def _compute_is_consignment(self):
        for product in self:
            line = self.env['consignment.contract.line'].sudo().search([
                ('product_id', '=', product.id),
                ('contract_id.state', '=', 'active')
            ], limit=1)
            product.is_consignment = bool(line)

class PosSession(models.Model):
    _inherit = "pos.session"

    def _loader_params_product_product(self):
        res = super(PosSession, self)._loader_params_product_product()
        if 'search_params' in res and 'fields' in res['search_params']:
            # ensure the field is included; avoid duplicates
            if 'is_consignment' not in res['search_params']['fields']:
                res['search_params']['fields'] += ['is_consignment']
        return res

    def _get_pos_ui_product_product(self, params):
        products = super(PosSession, self)._get_pos_ui_product_product(params)
        ContractLine = self.env['consignment.contract.line'].sudo()
        for prod in products:
            try:
                line = ContractLine.search([('product_id','=', prod['id']), ('contract_id.state','=','active')], limit=1)
                if line:
                    prod['consignment_contract_id'] = line.contract_id.id
                    prod['consignment_supplier_id'] = line.contract_id.partner_id.id
                    prod['is_consignment'] = True
                else:
                    prod['is_consignment'] = False
            except Exception as e:
                _logger.error('Error adding consignment data: %s', e)
        return products

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    consignment_contract_id = fields.Many2one('consignment.contract', string='Consignment Contract')
    consignment_supplier_id = fields.Many2one('res.partner', string='Consignment Supplier')

    @api.model
    def _order_line_fields(self, line, session_id=None):
        fields = super(PosOrderLine, self)._order_line_fields(line, session_id)
        vals = fields[2]
        if line.get('consignment_contract_id'):
            vals['consignment_contract_id'] = line.get('consignment_contract_id')
        if line.get('consignment_supplier_id'):
            vals['consignment_supplier_id'] = line.get('consignment_supplier_id')
        return fields

class PosConsignmentSale(models.Model):
    _name = 'pos.consignment.sale'
    _description = 'POS Consignment Sale Log'

    pos_order_id = fields.Many2one('pos.order', 'POS Order')
    product_id = fields.Many2one('product.product', 'Product')
    supplier_id = fields.Many2one('res.partner', 'Supplier')
    contract_id = fields.Many2one('consignment.contract', 'Contract')
    qty = fields.Float('Quantity')
    unit_price = fields.Float('Unit Price')
    subtotal = fields.Monetary('Subtotal')
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
