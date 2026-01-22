import logging
from datetime import datetime
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _

import base64

_logger = logging.getLogger(__name__)


class mix_and_match_combination_file(models.Model):
    _name= "mix.and.match.comb.file"
    _rec_name="filename"

    def _rows(self, line):
        data = {
            'mm_type': line[0:1],
            'promo_no' : line[1:13],
            'mm_start_date' : line[13:21],
            'mm_end_date' : line[21:29],
            'mm_start_time' : line[29:33],
            'mm_end_time' : line[33:37],
            'plu_count' : line[37:45],
            'promo_qty' : line[45:55],
            'promo_qty1' : line[53:59],
            'promo_qty2': line[59:65],
            'promo_qty3': line[65:71],
            'promo_qty4': line[71:77],
            'promo_qty5': line[77:83],
            'promo_qty6': line[83:89],
            'sku1': line[89:102],  
            'sku2': line[102:115],
            'sku3': line[115:128],
            'sku4': line[128:141],
            'sku5': line[141:154],
            'sku6': line[154:167],
            'promo_price1': line[167:184],
            'promo_price2': line[184:201],
            'promo_price3': line[201:218],
            'promo_price4': line[218:235],
            'promo_price5': line[235:252],
            'promo_price6': line[252:269],
            'total_promo_price': line[269:286],
            'promo_description': line[286:299],
            'record_flag': line[299:300],
            'end_of_record': line[300:301]
        }
        return data

    def check_mix_and_match_comb(self, mm_comb_code):
        res = self.env['pos.promotion'].search([('promotion_code','=', mm_comb_code)], limit=1)
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
    
    def check_promotion_line(self, promotion_id, product_id):
        res = self.env['fixed.price.multi.products'].search([('promotion_id','=', promotion_id), ('product_ids','in', product_id),], limit=1)
        if res:
            mes = True
            return mes
        else:
            mes = False
            return mes

    def create_mix_and_match_comb(self, rows, store_id): 
        products_mes1, product_1 = self.check_product(rows['sku1'].replace(" ", ""))
        products_mes2, product_2 = self.check_product(rows['sku2'].replace(" ", ""))
        products_mes3, product_3 = self.check_product(rows['sku3'].replace(" ", ""))
        products_mes4, product_4 = self.check_product(rows['sku4'].replace(" ", ""))
        products_mes5, product_5 = self.check_product(rows['sku5'].replace(" ", ""))
        products_mes6, product_6 = self.check_product(rows['sku6'].replace(" ", ""))
        start_date = rows['mm_start_date'].replace(" ","")
        start_date = str(start_date[:4]) + "-" + str(start_date[4:6]).zfill(2) + "-" + str(start_date[6:]).zfill(2)
        end_date = rows['mm_end_date'].replace(" ","")
        end_date = str(end_date[:4]) + "-" + str(end_date[4:6]).zfill(2) + "-" + str(end_date[6:]).zfill(2)
        from_time = int(rows['mm_start_time'][:2] or "")
        to_time = int(rows['mm_end_time'][:2] or "")
        products = []
        if products_mes1:
            products.append(product_1.id)
        if products_mes2:
            products.append(product_2.id)
        if products_mes3:
            products.append(product_3.id)
        if products_mes4:
            products.append(product_4.id)
        if products_mes5:
            products.append(product_5.id)
        if products_mes6:
            products.append(product_6.id)
        vals = {
            'active': True,
            'promotion_code': rows['promo_no'].replace(" ", ""),
            'promotion_type': "fixed_price_on_multi_product",
            'branch_ids': [store_id],
            'from_date': start_date,
            'to_date': end_date,
            'from_time': "{}".format(from_time),
            'to_time': "{}".format(to_time),
            'multi_products_fixed_price_ids': [(0,0, {
                            'product_ids': products,
                            'fixed_price': rows['total_promo_price'],
                        })]
        }
        _logger.info("CREATE MM COMBINATION")
        _logger.info(vals)
        res = self.env['pos.promotion'].create(vals)

    def update_mix_and_match_comb(self, rows, promotion_id, store_id):
        res = self.env['pos.promotion'].search([('id','=', promotion_id)])
        products_mes1, product_1 = self.check_product(rows['sku1'].replace(" ", ""))
        products_mes2, product_2 = self.check_product(rows['sku2'].replace(" ", ""))
        products_mes3, product_3 = self.check_product(rows['sku3'].replace(" ", ""))
        products_mes4, product_4 = self.check_product(rows['sku4'].replace(" ", ""))
        products_mes5, product_5 = self.check_product(rows['sku5'].replace(" ", ""))
        products_mes6, product_6 = self.check_product(rows['sku6'].replace(" ", ""))
        start_date = rows['mm_start_date'].replace(" ","")
        start_date = str(start_date[:4]) + "-" + str(start_date[4:6]).zfill(2) + "-" + str(start_date[6:]).zfill(2)
        end_date = rows['mm_end_date'].replace(" ","")
        end_date = str(end_date[:4]) + "-" + str(end_date[4:6]).zfill(2) + "-" + str(end_date[6:]).zfill(2)
        from_time = int(rows['mm_start_time'][:2])
        to_time = int(rows['mm_end_time'][:2])
        products = []
        if products_mes1:
            promo_line_mes1 = self.check_promotion_line(promotion_id, product_1.id)
            if promo_line_mes1 != True:
                products.append(product_1.id)
        if products_mes2:
            promo_line_mes2 = self.check_promotion_line(promotion_id, product_2.id)
            if promo_line_mes2 != True:
                products.append(product_2.id)
        if products_mes3:
            promo_line_mes3 = self.check_promotion_line(promotion_id, product_3.id)
            if promo_line_mes3 != True:
                products.append(product_3.id)
        if products_mes4:
            promo_line_mes4 = self.check_promotion_line(promotion_id, product_4.id)
            if promo_line_mes4 != True:
                products.append(product_4.id)
        if products_mes5:
            promo_line_mes5 = self.check_promotion_line(promotion_id, product_5.id)
            if promo_line_mes5 != True:
                products.append(product_5.id)
        if products_mes6:
            promo_line_mes6 = self.check_promotion_line(promotion_id, product_6.id)
            if promo_line_mes6 != True:
                products.append(product_6.id)
        vals = {
            'active': True,
            'promotion_code': rows['promo_no'].replace(" ", ""),
            'promotion_type': "fixed_price_on_multi_product",
            'from_date': start_date,
            'to_date': end_date,
            'from_time': "{}".format(from_time),
            'to_time': "{}".format(to_time),
        }
        promo_store_mes = self.check_promotion_store(promotion_id, store_id)
        if promo_store_mes != True:
            vals.update({'branch_ids': [(4, store_id)]})

        if len(products) != 0:
            vals.update({
                'multi_products_fixed_price_ids': [(0,0, {
                            'product_ids': products,
                            'fixed_price': rows['total_promo_price'],
                        })]
            })
        _logger.info("UPDATE MM COMBINATION")
        _logger.info(vals)
        res.write(vals)

    def generate_file(self):
        # Example : N5C31990.001
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

            store_mes, store = self.check_branch(store_code)
            if store_mes:
                check, promotion = self.check_mix_and_match_comb(rows['promo_no'].replace(" ", ""))
                if check:
                    self.update_mix_and_match_comb(rows, promotion.id, store.id)
                else:
                    self.create_mix_and_match_comb(rows, store.id)
            

    file = fields.Binary('File')
    filename = fields.Char('Filename', size=200)