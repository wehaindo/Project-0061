from odoo import models, fields, api
from odoo.addons.weha_ginee_integration.libs.lib_ginee import GineeClient


import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def sync_with_ginee(self):
        # ginee_client = GineeClient(self.env['ir.config_parameter'].sudo().get_param('ginee.access_key'),
        #                             self.env['ir.config_parameter'].sudo().get_param('ginee.secret_key'))
        ginee_client = GineeClient('b841f5efb1c46cf6','642859cbe0f3a7e4')
        products = ginee_client.get_products()
        _logger.info(products)
        # for product in products:
        #     self.create({
        #         'name': product['name'],
        #         'list_price': product['price'],
        #         'description': product['description'],
        #     })

    def sync_to_ginee(self):
        ginee_client = GineeClient(self.env['ir.config_parameter'].sudo().get_param('ginee.access_key'),
                                    self.env['ir.config_parameter'].sudo().get_param('ginee.secret_key'))
        for product in self:
            product_data = {
                'name': product.name,
                'price': product.list_price,
                'description': product.description,
            }
            if not product.ginee_id:
                ginee_product = ginee_client.create_product(product_data)
                product.ginee_id = ginee_product['id']
            else:
                ginee_client.update_product(product.ginee_id, product_data)