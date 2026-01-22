import logging
from datetime import datetime
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _
import threading
import base64

_logger = logging.getLogger(__name__)

class mix_and_match_partial_file(models.Model):
    _inherit= "mix.and.match.partial.file"

    def create_mix_and_match_partial_with_line(self, line, rows, promotion):
        try:
            if rows['mm_type']:
                products_mes, products = self.check_product(rows['sku_no'])
                if products_mes:
                    # BUY 1 GET PRICE
                    if rows['mm_type'] == "Q":                        
                        if int(rows['mm_fix_foc_qty']) == 0:
                            pos_quantity_fixed_price_id = self.env['quantity.fixed.price'].search([('pos_promotion_id','=',promotion.id),('product_id','=', products.id)])
                            pos_quantity_fixed_price_id.unlink()    
                            vals = {
                                'pos_quantity_fixed_price_ids': [(0,0, {
                                    'product_id': products.id,
                                    'quantity_amt': int(rows['mm_qty']),
                                    'fixed_price': rows['promo_price'],
                                })]
                            }
                            promotion.write(vals)                            
                        else:
                            # BUY 1 GET 1
                            pos_quantity_fixed_price_id = self.env['quantity.fixed.price'].search([('pos_promotion_id','=',promotion.id),('product_id','=', products.id)])
                            pos_quantity_fixed_price_id.unlink()
                            vals = {
                                'pos_condition_ids': [(0,0, {
                                    'product_x_id': products.id,
                                    'operator': "greater_than_or_eql",
                                    'quantity': int(rows['mm_qty']),
                                    'product_y_id': products.id,
                                    'quantity_y': int(rows['mm_fix_foc_qty']),
                                })]
                            }
                            promotion.write(vals)

                    if rows['mm_type'] == "P":
                        if int(rows['mm_fix_foc_qty']) == 0:
                            if len(promotion.pos_partial_quantity_fixed_price_ids) == 0:                                
                                vals = {
                                    'pos_partial_quantity_fixed_price_ids': [(0,0, {
                                        'product_ids': [products.id],
                                        'quantity': int(rows['mm_qty']),
                                        'quantity_amt': int(rows['mm_fix_foc_qty']),
                                        'fixed_price': rows['promo_price'],
                                    })]
                                }
                                promotion.write(vals)
                                promotion_line = {
                                    'product_id': products,
                                    'quantity': int(rows['mm_qty']),
                                    'quantity_amt': int(rows['mm_fix_foc_qty']),
                                    'fixed_price': int(rows['promo_price'].split('.')[0]),
                                }
                                promotion.generate_decentralize_by_branch_for_partial('C', promotion_line)
                            else:
                                promotion.pos_partial_quantity_fixed_price_ids[0].product_ids = [(4, products.id)]                                                         
                                promotion_line = {
                                    'product_id': products,
                                    'quantity': int(rows['mm_qty']),
                                    'quantity_amt': int(rows['mm_fix_foc_qty']),
                                    'fixed_price': int(rows['promo_price'].split('.')[0]),
                                }
                                promotion.generate_decentralize_by_branch_for_partial('W', promotion_line)
                        else:
                            if len(promotion.pos_partial_quantity_fixed_price_ids) == 0:
                                vals = {
                                    'pos_partial_quantity_fixed_price_ids': [(0,0, {
                                        'product_ids': [products.id],
                                        'quantity': int(rows['mm_qty']),
                                        'quantity_amt': int(rows['mm_fix_foc_qty']),
                                        'fixed_price': rows['promo_price'],
                                    })]
                                }
                                promotion.write(vals)
                                promotion_line = {
                                    'product_id': products,
                                    'quantity': int(rows['mm_qty']),
                                    'quantity_amt': int(rows['mm_fix_foc_qty']),
                                    'fixed_price': int(rows['promo_price'].split('.')[0]),
                                }
                                promotion.generate_decentralize_by_branch_for_partial('C', promotion_line)
                            else:
                                promotion.pos_partial_quantity_fixed_price_ids[0].product_ids = [(4, products.id)]               
                                promotion_line = {
                                    'product_id': products,
                                    'quantity': int(rows['mm_qty']),
                                    'quantity_amt': int(rows['mm_fix_foc_qty']),
                                    'fixed_price': int(rows['promo_price'].split('.')[0]),
                                }
                                promotion.generate_decentralize_by_branch_for_partial('W', promotion_line)
                line.state = "done"                                
            else:
                line.state = "error"
                line.err_msg = "Promotion type not found"                
        except Exception as e:
            line.state = 'error'
            line.err_msg = str(e)

    def update_mix_and_match_partial_with_line(self, line, rows, promotion, products, store_id):
        try:
            _logger.info("UPDATE PROMOTION")
            if rows['mm_type'] == "Q":
                if int(rows['mm_fix_foc_qty']) == 0:
                    pos_quantity_fixed_price_id = self.env['quantity.fixed.price'].search([('pos_promotion_id','=',promotion.id),('product_id','=', products.id)])
                    pos_quantity_fixed_price_id.unlink()                                                            
                    vals = {
                        'pos_quantity_fixed_price_ids': [(0,0, {
                            'product_id': products.id,
                            'quantity_amt': int(rows['mm_qty']),
                            'fixed_price': rows['promo_price'],
                        })]
                    }
                    promotion.write(vals)   
                    line.state = "done"
                    line.err_msg = "Success"                 
                else:
                    pos_quantity_fixed_price_id = self.env['quantity.fixed.price'].search([('pos_promotion_id','=',promotion.id),('product_id','=', products.id)])
                    pos_quantity_fixed_price_id.unlink()
                    vals = {
                        'pos_condition_ids': [(0,0, {
                            'product_x_id': products.id,
                            'operator': "greater_than_or_eql",
                            'quantity': int(rows['mm_qty']),
                            'product_y_id': products.id,
                            'quantity_y': int(rows['mm_fix_foc_qty']),
                        })]
                    }
                    promotion.write(vals)
                    line.state = "done"
                    line.err_msg = "Success"
            
            if rows['mm_type'] == "P":
                # buy_x_partial_quantity_get_special_price           
                if len(promotion.pos_partial_quantity_fixed_price_ids) > 0:
                    pos_partial_quantity_fixed_price_id = promotion.pos_partial_quantity_fixed_price_ids[0]
                    pos_partial_quantity_fixed_price_id.product_ids = [(4, products.id)]
                    line.state = "done"
                    line.err_msg = "Success"
                    promotion_line = {
                        'product_id': products,
                        'quantity': int(rows['mm_qty']),
                        'quantity_amt': int(rows['mm_fix_foc_qty']),
                        'fixed_price': int(rows['promo_price'].split('.')[0]),
                    }
                    promotion.generate_decentralize_by_branch_for_partial('W', promotion_line)
                else:    
                    vals = {
                        'pos_partial_quantity_fixed_price_ids': [(0,0, {
                            'product_ids': [products.id],
                            'quantity': int(rows['mm_qty']),
                            'quantity_amt': int(rows['mm_fix_foc_qty']),
                            'fixed_price': rows['promo_price'],
                        })]
                    }
                    promotion.write(vals)
                    line.state = "done"
                    line.err_msg = "Success"
                    promotion_line = {
                        'product_id': products,
                        'quantity': int(rows['mm_qty']),
                        'quantity_amt': int(rows['mm_fix_foc_qty']),
                        'fixed_price': int(rows['promo_price'].split('.')[0]),
                    }
                    promotion.generate_decentralize_by_branch_for_partial('W', promotion_line)

        except Exception as e:
            line.state = "error"        
            line.err_msg = str(e)