from odoo import models, fields, api
from odoo.addons.weha_ginee_integration.libs.lib_ginee import GineeClient


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def sync_with_ginee(self):
        ginee_client = GineeClient(self.env['ir.config_parameter'].sudo().get_param('ginee.access_key'),
                                    self.env['ir.config_parameter'].sudo().get_param('ginee.secret_key'))
        orders = ginee_client.get_orders()
        for order in orders:
            self.create({
                'partner_id': self.env['res.partner'].search([('name', '=', order['customer_name'])], limit=1).id,
                'date_order': order['order_date'],
                'amount_total': order['total_amount'],
            })