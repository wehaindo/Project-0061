import logging
from datetime import datetime
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _
import threading
import base64

_logger = logging.getLogger(__name__)


class mix_and_match_combination_file(models.Model):
    _inherit= "mix.and.match.comb.file"
    
    def create_mix_and_match_comb_with_line(self, line, rows, promotion):
        try:            
            for combination_product_fixed_price_id  in promotion.combination_product_fixed_price_ids:
                combination_product_fixed_price_id.unlink()
            products_mes1, product_1 = self.check_product(rows['sku1'])
            _logger.info(products_mes1)
            products_mes2, product_2 = self.check_product(rows['sku2'])
            _logger.info(products_mes2)
            products_mes3, product_3 = self.check_product(rows['sku3'])
            _logger.info(products_mes3)
            products_mes4, product_4 = self.check_product(rows['sku4'])
            _logger.info(products_mes4)
            products_mes5, product_5 = self.check_product(rows['sku5'])
            _logger.info(products_mes5)
            products_mes6, product_6 = self.check_product(rows['sku6'])
            _logger.info(products_mes6)
            # if product_1 and product_2 and product_3 and product_4 and product_5 and product_6:
            _logger.info('create_mix_and_match_comb')
            products = []
            promotion_products = []
            if products_mes1:
                products.append(
                    (0,0, {
                        'product_id': product_1.id,
                        'quantity_amt': rows['promo_qty1'],
                        'fixed_price': rows['promo_price1'],
                    })
                )
                promotion_products.append({
                    'product_id': product_1,
                    'quantity_amt': rows['promo_qty1'],
                    'fixed_price': rows['promo_price1'],
                })
            if products_mes2:
                products.append(
                    (0,0, {
                        'product_id': product_2.id,
                        'quantity_amt': rows['promo_qty2'],
                        'fixed_price': rows['promo_price2'],
                    })
                )
                promotion_products.append({
                    'product_id': product_2,
                    'quantity_amt': rows['promo_qty2'],
                    'fixed_price': rows['promo_price2'],
                })
            if products_mes3:
                products.append(
                    (0,0, {
                        'product_id': product_3.id,
                        'quantity_amt': rows['promo_qty3'],
                        'fixed_price': rows['promo_price3'],
                    })
                )
                promotion_products.append({
                    'product_id': product_3,
                    'quantity_amt': rows['promo_qty3'],
                    'fixed_price': rows['promo_price3'],
                })
            if products_mes4:
                products.append(
                    (0,0, {
                        'product_id': product_4.id,
                        'quantity_amt': rows['promo_qty4'],
                        'fixed_price': rows['promo_price4'],
                    })
                )
                promotion_products.append({
                    'product_id': product_4,
                    'quantity_amt': rows['promo_qty4'],
                    'fixed_price': rows['promo_price4'],
                })
            if products_mes5:
                products.append(
                    (0,0, {
                        'product_id': product_5.id,
                        'quantity_amt': rows['promo_qty5'],
                        'fixed_price': rows['promo_price5'],
                    })
                )
                promotion_products.append({
                    'product_id': product_5,
                    'quantity_amt': rows['promo_qty5'],
                    'fixed_price': rows['promo_price5'],
                })
            if products_mes6:
                products.append(
                    (0,0, {
                        'product_id': product_6.id,
                        'quantity_amt': rows['promo_qty6'],
                        'fixed_price': rows['promo_price6'],
                    })
                )
                promotion_products.append({
                    'product_id': product_6,
                    'quantity_amt': rows['promo_qty6'],
                    'fixed_price': rows['promo_price6'],
                })
            _logger.info(products)
            promotion.write({'combination_product_fixed_price_ids': products})
            line.state = "done"
            line.err_msg = "Success"                    
            _logger.info('create promotion.generate_decentralize_by_branch_for_combination')                                    
            _logger.info(promotion_products)
            promotion.generate_decentralize_by_branch_for_combination('C', promotion_products)
        except Exception as e:
            line.state = 'error'
            line.err_msg = str(e)
            _logger.error(e)
        
    def update_mix_and_match_comb_with_line(self, line, rows, promotion):  
        try:
            for combination_product_fixed_price_id  in promotion.combination_product_fixed_price_ids:
                combination_product_fixed_price_id.unlink()

            products_mes1, product_1 = self.check_product(rows['sku1'])
            products_mes2, product_2 = self.check_product(rows['sku2'])
            products_mes3, product_3 = self.check_product(rows['sku3'])
            products_mes4, product_4 = self.check_product(rows['sku4'])
            products_mes5, product_5 = self.check_product(rows['sku5'])
            products_mes6, product_6 = self.check_product(rows['sku6'])
            products = []
            promotion_products = []
            if products_mes1:
                products.append(
                    (0,0, {
                        'product_id': product_1.id,
                        'quantity_amt': rows['promo_qty1'],
                        'fixed_price': rows['promo_price1'],
                    })
                )
                promotion_products.append({
                    'product_id': product_1,
                    'quantity_amt': rows['promo_qty1'],
                    'fixed_price': rows['promo_price1'],
                })
            if products_mes2:
                products.append(
                    (0,0, {
                        'product_id': product_2.id,
                        'quantity_amt': rows['promo_qty2'],
                        'fixed_price': rows['promo_price2'],
                    })
                )
                promotion_products.append({
                    'product_id': product_2,
                    'quantity_amt': rows['promo_qty2'],
                    'fixed_price': rows['promo_price2'],
                })

            if products_mes3:
                products.append(
                    (0,0, {
                        'product_id': product_3.id,
                        'quantity_amt': rows['promo_qty3'],
                        'fixed_price': rows['promo_price3'],
                    })
                )
                promotion_products.append({
                    'product_id': product_3,
                    'quantity_amt': rows['promo_qty3'],
                    'fixed_price': rows['promo_price3'],
                })
            if products_mes4:
                products.append(
                    (0,0, {
                        'product_id': product_4.id,
                        'quantity_amt': rows['promo_qty4'],
                        'fixed_price': rows['promo_price4'],
                    })
                )
                promotion_products.append({
                    'product_id': product_4,
                    'quantity_amt': rows['promo_qty4'],
                    'fixed_price': rows['promo_price4'],
                })
            if products_mes5:
                products.append(
                    (0,0, {
                        'product_id': product_5.id,
                        'quantity_amt': rows['promo_qty5'],
                        'fixed_price': rows['promo_price5'],
                    })
                )
                promotion_products.append({
                    'product_id': product_5,
                    'quantity_amt': rows['promo_qty5'],
                    'fixed_price': rows['promo_price5'],
                })
            if products_mes6:
                products.append(
                    (0,0, {
                        'product_id': product_6.id,
                        'quantity_amt': rows['promo_qty6'],
                        'fixed_price': rows['promo_price6'],
                    })
                )
                promotion_products.append({
                    'product_id': product_6,
                    'quantity_amt': rows['promo_qty6'],
                    'fixed_price': rows['promo_price6'],
                })
            _logger.info(products)
            promotion.write({'combination_product_fixed_price_ids': products})
            line.state = "done"
            line.err_msg = "Success"
            _logger.info('update promotion.generate_decentralize_by_branch_for_combination')                                    
            _logger.info(promotion_products)
            promotion.generate_decentralize_by_branch_for_combination('W', promotion_products)
        except Exception as e:
            line.state = "error"
            line.err_msg = str(e)
            _logger.error(e)
