from odoo import api, fields, models


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        # result['search_params']['fields'].extend(
        #     ['qty_available', 'virtual_available', 'outgoing_qty', 'type',
        #      'setu_alternative_products', 'name', 'product_template_attribute_value_ids'])
        return result

