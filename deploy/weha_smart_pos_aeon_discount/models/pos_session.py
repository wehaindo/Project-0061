from odoo import models, fields, api, _ 

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].append('is_member_discount')
        result['search_params']['fields'].append('member_discount_percentage')
        result['search_params']['fields'].append('is_member_day_discount')
        result['search_params']['fields'].append('member_day_discount_percentage')
        return result
    
    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        result.append('product.category')            
        return result
    
    def _loader_params_product_category(self):
        result = super(PosSession, self)._loader_params_product_category()
        result['search_params']['fields'].append('is_member_discount')
        result['search_params']['fields'].append('member_discount_percentage')
        result['search_params']['fields'].append('is_member_day_discount')
        result['search_params']['fields'].append('member_day_discount_percentage')
        return result
