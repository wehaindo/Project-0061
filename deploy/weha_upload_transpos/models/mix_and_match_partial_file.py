import logging
from datetime import datetime
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _

import base64

_logger = logging.getLogger(__name__)


class mix_and_match_partial_file(models.Model):
    _name= "mix.and.match.partial.file"
    _rec_name="filename"

    def _rows(self, line):
        data = {
            'mm_type': line[0:1],
            'promo_no' : line[1:13],
            'sku_no' : line[13:26],
            'mm_qty' : line[26:34],
            'mm_start_date' : line[34:42],
            'mm_end_date' : line[42:50],
            'mm_start_time' : line[50:54],
            'mm_end_time' : line[54:58],
            'mm_fix_foc_qty' : line[58:60],
            'promo_price' : line[60:77],
            'promo_disc_name' : line[77:90],
            'record_flag': line[90:92],
            'end_of_record': line[92:94]
        }
        return data
    
    def check_mix_and_match_partial(self, mm_partial_code):
        res = self.env['pos.promotion'].search([('promotion_code','=', mm_partial_code)], limit=1)
        if res:
            mes = True
            return mes, res
        else:
            mes = False
            return mes, res
    
    def check_mix_and_match_partial_line(self, promotion_type, promotion_id, product_id):
        
        if promotion_type == "buy_x_quantity_get_special_price":
            res = self.env['quantity.fixed.price'].search([('pos_promotion_id','=', promotion_id), ('product_id','=', product_id),], limit=1)
            if res:
                mes = True
                return mes, res
            else:
                mes = False
                return mes, res
        
        if promotion_type == "buy_x_get_y":
            res = self.env['pos.conditions'].search([('pos_promotion_rel','=', promotion_id), ('product_x_id','=', product_id),], limit=1)
            if res:
                mes = True
                return mes, res
            else:
                mes = False
                return mes, res

    def check_product(self, sku_no):
        products = self.env['product.template'].search([('default_code','=', sku_no)], limit=1)
        if products:
            mes = True
            return mes, products
        else:
            mes = False
            return mes, products
    
    def check_branch(self, store_no):
        store = self.env['res.branch'].search([('code','=', store_no)], limit=1)
        if store:
            mes = True
            return mes, store
        else:
            mes = False
            return mes, store
    
    def check_promotion_store(self, promotion_id, store_id):
        promo = self.env['pos.promotion'].search([('id','=', promotion_id), ('branch_ids','in', store_id)], limit=1)
        if promo:
            mes = True
            return mes
        else:
            mes = False
            return mes
    
    def create_mix_and_match_partial(self, rows, store_id):
        products_mes, products = self.check_product(rows['sku_no'].replace(" ", ""))
        if products_mes:
            start_date = rows['mm_start_date'].replace(" ","")
            start_date = str(start_date[:4]) + "-" + str(start_date[4:6]).zfill(2) + "-" + str(start_date[6:]).zfill(2)
            end_date = rows['mm_end_date'].replace(" ","")
            end_date = str(end_date[:4]) + "-" + str(end_date[4:6]).zfill(2) + "-" + str(end_date[6:]).zfill(2)
            from_time = int(rows['mm_start_time'][:2])
            to_time = int(rows['mm_end_time'][:2])

            vals = {
                'active': True,
                'promotion_code': rows['promo_no'].replace(" ",""),
                'branch_ids': [store_id],
                'from_date': start_date,
                'to_date': end_date,
                'from_time': "{}".format(from_time),
                'to_time': "{}".format(to_time),
            }

            # BUY 1 GET PRICE
            if rows['mm_type'] == "Q":

                if int(rows['mm_fix_foc_qty']) == 0:
                    vals.update({
                        'promotion_type': "buy_x_quantity_get_special_price",
                        'pos_quantity_fixed_price_ids': [(0,0, {
                                        'product_id': products.id,
                                        'quantity_amt': int(rows['mm_qty'].replace(" ","")),
                                        'fixed_price': rows['promo_price'],
                                    })]
                    })
                else:
                    # BUY 1 GET 1
                    vals.update({
                        'promotion_type': "buy_x_get_y",
                        'pos_condition_ids': [(0,0, {
                                        'product_x_id': products.id,
                                        'operator': "greater_than_or_eql",
                                        'quantity': int(rows['mm_qty'].replace(" ","")),
                                        'product_y_id': products.id,
                                        'quantity_y': int(rows['mm_fix_foc_qty']),
                                    })]
                    })

            if rows['mm_type'] == "P":

                if int(rows['mm_fix_foc_qty']) == 0:
                    pass
                else:
                    vals.update({
                        'promotion_type': "fixed_price_on_multi_product",
                        'multi_products_fixed_price_ids': [(0,0, {
                            'product_ids': [products.id],
                            'fixed_price': rows['total_promo_price'],
                        })]
                    })

            _logger.info("CREATE PROMOTION")
            _logger.info(vals)
            res = self.env['pos.promotion'].create(vals)

    def update_mix_and_match_partial(self, rows, mm_partial_id, promotion_type, product_id, store_id):
        products_mes, products = self.check_product(rows['sku_no'].replace(" ", ""))
        if products_mes:
            res = self.env['pos.promotion'].search([('id','=', mm_partial_id)])
            start_date = rows['mm_start_date'].replace(" ","")
            start_date = str(start_date[:4]) + "-" + str(start_date[4:6]).zfill(2) + "-" + str(start_date[6:]).zfill(2)
            end_date = rows['mm_end_date'].replace(" ","")
            end_date = str(end_date[:4]) + "-" + str(end_date[4:6]).zfill(2) + "-" + str(end_date[6:]).zfill(2)
            from_time = int(rows['mm_start_time'][:2])
            to_time = int(rows['mm_end_time'][:2])

            vals = {
                'from_date': start_date,
                'to_date': end_date,
                'from_time': "{}".format(from_time),
                'to_time': "{}".format(to_time),
            }

            promo_store_mes = self.check_promotion_store(mm_partial_id, store_id)
            if promo_store_mes != True:
                vals.update({'branch_ids': [(4, store_id)]})

            promotion_line_mes, promotion_line = self.check_mix_and_match_partial_line(promotion_type, mm_partial_id, product_id)
            if promotion_line_mes:
                _logger.info("UPDATE PROMOTION LINE")
                # UPDATE PROMOTION LINE
                # BUY 1 GET PRICE
                if rows['mm_type'] == "Q":

                    if int(rows['mm_fix_foc_qty']) == 0:
                        vals.update({
                            'pos_quantity_fixed_price_ids': [(1,products.id, {
                                            'product_id': products.id,
                                            'quantity_amt': int(rows['mm_qty'].replace(" ","")),
                                            'fixed_price': rows['promo_price'],
                                        })]
                        })
                    else:
                        # BUY 1 GET 1
                        vals.update({
                            'pos_condition_ids': [(1,products.id, {
                                            'product_x_id': products.id,
                                            'operator': "greater_than_or_eql",
                                            'quantity': int(rows['mm_qty'].replace(" ","")),
                                            'product_y_id': products.id,
                                            'quantity_y': int(rows['mm_fix_foc_qty']),
                                        })]
                        })
                
                if rows['mm_type'] == "P":

                    if int(rows['mm_fix_foc_qty']) == 0:
                        pass
                    else:
                        vals.update({
                            'multi_products_fixed_price_ids': [(1,mm_partial_id, {
                                'product_ids': [(4, products.id)],
                                'fixed_price': rows['total_promo_price'],
                            })]
                        })

            else:
                _logger.info("CREATE PROMOTION LINE")
                # CREATE PROMOTION LINE
                # BUY 1 GET PRICE
                if rows['mm_type'] == "Q":

                    if int(rows['mm_fix_foc_qty']) == 0:
                        # 'promotion_type': "buy_x_quantity_get_special_price",
                        vals.update({
                            'pos_quantity_fixed_price_ids': [(0,0, {
                                            'product_id': products.id,
                                            'quantity_amt': int(rows['mm_qty'].replace(" ","")),
                                            'fixed_price': rows['promo_price'],
                                        })]
                        })
                    else:
                        # BUY 1 GET 1
                        # 'promotion_type': "buy_x_get_y",
                        vals.update({
                            'pos_condition_ids': [(0,0, {
                                            'product_x_id': products.id,
                                            'operator': "greater_than_or_eql",
                                            'quantity': int(rows['mm_qty'].replace(" ","")),
                                            'product_y_id': products.id,
                                            'quantity_y': int(rows['mm_fix_foc_qty']),
                                        })]
                        })

                if rows['mm_type'] == "P":

                    if int(rows['mm_fix_foc_qty']) == 0:
                        pass
                    else:
                        vals.update({
                            'multi_products_fixed_price_ids': [(1,mm_partial_id, {
                                'product_ids': [(4, products.id)],
                                'fixed_price': rows['total_promo_price'],
                            })]
                        })

            _logger.info("UPDATE PROMOTION")
            _logger.info(vals)
            res.write(vals)

    def generate_file(self):
        # Example : M5C31990.001
        filename = self.filename
        filename = filename.replace(".","")
        store_code = filename[7:11]
        _logger.info(store_code)

        file_content = base64.b64decode(self.file)
        file_content = file_content.decode("utf-8")
        file_lines = file_content.split("\r\n")

        for line in file_lines:
            _logger.info(str(len(line)))
            rows = self._rows(line)
            _logger.info(rows)
            
            # Check Store is ready?
            store_mes, store = self.check_branch(store_code)
            if store_mes:
                # Check Product is ready?
                products_mes, products = self.check_product(rows['sku_no'].replace(" ", ""))
                if products_mes:
                    # Check Promotion is ready?
                    promotion_mes, promotion = self.check_mix_and_match_partial(rows['promo_no'].replace(" ", ""))
                    if promotion_mes:
                        self.update_mix_and_match_partial(rows, promotion.id, promotion.promotion_type, products.id, store.id)
                    else:
                        self.create_mix_and_match_partial(rows, store.id)
        

    file = fields.Binary('File')
    filename = fields.Char('Filename', size=200)