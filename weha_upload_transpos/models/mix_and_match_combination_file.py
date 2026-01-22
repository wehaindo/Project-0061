import logging
from datetime import datetime
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _
import threading
import base64

_logger = logging.getLogger(__name__)


class mix_and_match_combination_file(models.Model):
    _name= "mix.and.match.comb.file"
    _rec_name="filename"
    _order = "date_start desc"
    
    @api.depends('mix_and_match_comb_line_ids')
    def get_lines_count(self):
        for row in self:
            row.lines_count = len(row.mix_and_match_comb_line_ids)

    def action_view_lines(self):
        return {
            'name': _('Lines'),
            'res_model': 'mix.and.match.comb.line',
            'view_mode': 'tree,form',
            'views': [
                (self.env.ref('weha_upload_transpos.view_mix_and_match_comb_line_tree').id, 'tree'),
                (self.env.ref('weha_upload_transpos.view_mix_and_match_comb_line_form').id, 'form'),
                ],
            'type': 'ir.actions.act_window',
            'domain': [('mix_and_match_comb_file_id', 'in', self.ids)],
        }

    def _rows(self, line):
        data = {
            'mm_type': line[0:1].strip(),
            'promo_no' : line[1:13].strip(),
            'mm_start_date' : line[13:21].strip(),
            'mm_end_date' : line[21:29].strip(),
            'mm_start_time' : line[29:33].strip(),
            'mm_end_time' : line[33:37].strip(),
            'plu_count' : line[37:45].strip(),
            'promo_qty' : line[45:55].strip(),
            'promo_qty1' : line[53:59].strip(),
            'promo_qty2': line[59:65].strip(),
            'promo_qty3': line[65:71].strip(),
            'promo_qty4': line[71:77].strip(),
            'promo_qty5': line[77:83].strip(),
            'promo_qty6': line[83:89].strip(),
            'sku1': line[89:102].strip(),  
            'sku2': line[102:115].strip(),
            'sku3': line[115:128].strip(),
            'sku4': line[128:141].strip(),
            'sku5': line[141:154].strip(),
            'sku6': line[154:167].strip(),
            'promo_price1': line[167:184].strip(),
            'promo_price2': line[184:201].strip(),
            'promo_price3': line[201:218].strip(),
            'promo_price4': line[218:235].strip(),
            'promo_price5': line[235:252].strip(),
            'promo_price6': line[252:269].strip(),
            'total_promo_price': line[269:286].strip(),
            'promo_description': line[286:299].strip(),
            'record_flag': line[299:300].strip(),
            'end_of_record': line[300:301].strip()
        }
        return data
 
    def check_store_promo(self, mm_comb_code, store):
        promotion_id = self.env['pos.promotion'].search([('promotion_code','=', mm_comb_code),('branch_ids','in', store.id)], limit=1)
        if promotion_id:
            mes = True
            return mes, promotion_id            
        else:
            mes = False
            return mes, ""

    def check_product(self, sku_no):
        products = self.env['product.template'].search([('default_code','=', sku_no)], limit=1)
        if products:
            product_product_id = self.env['product.product'].search([('product_tmpl_id','=', products.id)], limit=1)
            mes = True
            return mes, product_product_id
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
    
    def create_promo(self, rows, store):
        _logger.info("CREATE MM COMBINATION")
        start_date = rows['mm_start_date']
        start_date = str(start_date[:4]) + "-" + str(start_date[4:6]).zfill(2) + "-" + str(start_date[6:]).zfill(2)
        end_date = rows['mm_end_date']
        end_date = str(end_date[:4]) + "-" + str(end_date[4:6]).zfill(2) + "-" + str(end_date[6:]).zfill(2)
        from_time = int(rows['mm_start_time'][:2] or "")
        to_time = int(rows['mm_end_time'][:2] or "")
        promo_no = "{}{}".format(rows['mm_type'], rows['promo_no'])
        vals = {
            'active': True,
            'promotion_code': promo_no,
            'promotion_type': "combination_product_fixed_price",
            'branch_ids': [store.id],
            'from_date': start_date,
            'to_date': end_date,
            'from_time': "{}".format(from_time),
            'to_time': "{}".format(to_time),
            # 'combination_product_fixed_price_ids': products,
        }
        _logger.info(vals)
        promotion_id = self.env['pos.promotion'].create(vals)
        return True, promotion_id

    def update_promo(self, rows, promotion):
        start_date = rows['mm_start_date']
        start_date = str(start_date[:4]) + "-" + str(start_date[4:6]).zfill(2) + "-" + str(start_date[6:]).zfill(2)
        end_date = rows['mm_end_date']
        end_date = str(end_date[:4]) + "-" + str(end_date[4:6]).zfill(2) + "-" + str(end_date[6:]).zfill(2)
        from_time = int(rows['mm_start_time'][:2] or "")
        to_time = int(rows['mm_end_time'][:2] or "")
        vals = {            
            'from_date': start_date,
            'to_date': end_date,
            'from_time': "{}".format(from_time),
            'to_time': "{}".format(to_time),
        }
        promotion.write(vals)
        
    def check_promotion_line(self, promotion_id, product_id):
        res = self.env['price.combination.products'].search([('promotion_id','=', promotion_id), ('product_id','=', product_id),], limit=1)
        if res:
            mes = True
            return mes
        else:
            mes = False
            return mes

    def create_mix_and_match_comb(self, rows, promotion): 
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
        if products_mes1:
            products.append(
                (0,0, {
                    'product_id': product_1.id,
                    'quantity_amt': rows['promo_qty1'],
                    'fixed_price': rows['promo_price1'],
                })
            )
        if products_mes2:
            products.append(
                (0,0, {
                    'product_id': product_2.id,
                    'quantity_amt': rows['promo_qty2'],
                    'fixed_price': rows['promo_price2'],
                })
            )
        if products_mes3:
            products.append(
                (0,0, {
                    'product_id': product_3.id,
                    'quantity_amt': rows['promo_qty3'],
                    'fixed_price': rows['promo_price3'],
                })
            )
        if products_mes4:
            products.append(
                (0,0, {
                    'product_id': product_4.id,
                    'quantity_amt': rows['promo_qty4'],
                    'fixed_price': rows['promo_price4'],
                })
            )
        if products_mes5:
            products.append(
                (0,0, {
                    'product_id': product_5.id,
                    'quantity_amt': rows['promo_qty5'],
                    'fixed_price': rows['promo_price5'],
                })
            )
        if products_mes6:
            products.append(
                (0,0, {
                    'product_id': product_6.id,
                    'quantity_amt': rows['promo_qty6'],
                    'fixed_price': rows['promo_price6'],
                })
            )

        promotion.write({'combination_product_fixed_price_ids': products})

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
            if products_mes1:
                products.append(
                    (0,0, {
                        'product_id': product_1.id,
                        'quantity_amt': rows['promo_qty1'],
                        'fixed_price': rows['promo_price1'],
                    })
                )
            if products_mes2:
                products.append(
                    (0,0, {
                        'product_id': product_2.id,
                        'quantity_amt': rows['promo_qty2'],
                        'fixed_price': rows['promo_price2'],
                    })
                )
            if products_mes3:
                products.append(
                    (0,0, {
                        'product_id': product_3.id,
                        'quantity_amt': rows['promo_qty3'],
                        'fixed_price': rows['promo_price3'],
                    })
                )
            if products_mes4:
                products.append(
                    (0,0, {
                        'product_id': product_4.id,
                        'quantity_amt': rows['promo_qty4'],
                        'fixed_price': rows['promo_price4'],
                    })
                )
            if products_mes5:
                products.append(
                    (0,0, {
                        'product_id': product_5.id,
                        'quantity_amt': rows['promo_qty5'],
                        'fixed_price': rows['promo_price5'],
                    })
                )
            if products_mes6:
                products.append(
                    (0,0, {
                        'product_id': product_6.id,
                        'quantity_amt': rows['promo_qty6'],
                        'fixed_price': rows['promo_price6'],
                    })
                )

            promotion.write({'combination_product_fixed_price_ids': products})
            line.state = "done"
            line.err_msg = "Success"            
        except Exception as e:
            line.state = 'error'
            line.err_msg = str(e)
            
    def update_mix_and_match_comb(self, rows, promotion):  
        for combination_product_fixed_price_id  in promotion.combination_product_fixed_price_ids:
            combination_product_fixed_price_id.unlink()
            
        products_mes1, product_1 = self.check_product(rows['sku1'])
        products_mes2, product_2 = self.check_product(rows['sku2'])
        products_mes3, product_3 = self.check_product(rows['sku3'])
        products_mes4, product_4 = self.check_product(rows['sku4'])
        products_mes5, product_5 = self.check_product(rows['sku5'])
        products_mes6, product_6 = self.check_product(rows['sku6'])
        products = []
        if products_mes1:
            products.append(
                (0,0, {
                    'product_id': product_1.id,
                    'quantity_amt': rows['promo_qty1'],
                    'fixed_price': rows['promo_price1'],
                })
            )
        if products_mes2:
            products.append(
                (0,0, {
                    'product_id': product_2.id,
                    'quantity_amt': rows['promo_qty2'],
                    'fixed_price': rows['promo_price2'],
                })
            )
        if products_mes3:
            products.append(
                (0,0, {
                    'product_id': product_3.id,
                    'quantity_amt': rows['promo_qty3'],
                    'fixed_price': rows['promo_price3'],
                })
            )
        if products_mes4:
            products.append(
                (0,0, {
                    'product_id': product_4.id,
                    'quantity_amt': rows['promo_qty4'],
                    'fixed_price': rows['promo_price4'],
                })
            )
        if products_mes5:
            products.append(
                (0,0, {
                    'product_id': product_5.id,
                    'quantity_amt': rows['promo_qty5'],
                    'fixed_price': rows['promo_price5'],
                })
            )
        if products_mes6:
            products.append(
                (0,0, {
                    'product_id': product_6.id,
                    'quantity_amt': rows['promo_qty6'],
                    'fixed_price': rows['promo_price6'],
                })
            )

        promotion.write({'combination_product_fixed_price_ids': products})

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
            if products_mes1:
                
                products.append(
                    (0,0, {
                        'product_id': product_1.id,
                        'quantity_amt': rows['promo_qty1'],
                        'fixed_price': rows['promo_price1'],
                    })
                )
            if products_mes2:
                products.append(
                    (0,0, {
                        'product_id': product_2.id,
                        'quantity_amt': rows['promo_qty2'],
                        'fixed_price': rows['promo_price2'],
                    })
                )
            if products_mes3:
                products.append(
                    (0,0, {
                        'product_id': product_3.id,
                        'quantity_amt': rows['promo_qty3'],
                        'fixed_price': rows['promo_price3'],
                    })
                )
            if products_mes4:
                products.append(
                    (0,0, {
                        'product_id': product_4.id,
                        'quantity_amt': rows['promo_qty4'],
                        'fixed_price': rows['promo_price4'],
                    })
                )
            if products_mes5:
                products.append(
                    (0,0, {
                        'product_id': product_5.id,
                        'quantity_amt': rows['promo_qty5'],
                        'fixed_price': rows['promo_price5'],
                    })
                )
            if products_mes6:
                products.append(
                    (0,0, {
                        'product_id': product_6.id,
                        'quantity_amt': rows['promo_qty6'],
                        'fixed_price': rows['promo_price6'],
                    })
                )

            promotion.write({'combination_product_fixed_price_ids': products})

            line.state = "done"
            line.err_msg = "Success"
        except Exception as e:
            line.state = "error"
            line.err_msg = str(e)

    def delete_mix_and_mathc_comb(self, rows, promotion):
        
        products_mes1, product_1 = self.check_product(rows['sku1'])
        products_mes2, product_2 = self.check_product(rows['sku2'])
        products_mes3, product_3 = self.check_product(rows['sku3'])
        products_mes4, product_4 = self.check_product(rows['sku4'])
        products_mes5, product_5 = self.check_product(rows['sku5'])
        products_mes6, product_6 = self.check_product(rows['sku6'])
        products = []
        if products_mes1:
            price_combination_product_id = self.env['price.combination.products'].search([('promotion_id','=',promotion.id),('product_id','=', product_1.id)], limit=1)
            if price_combination_product_id:
                price_combination_product_id.unlink()

        if products_mes2:
            price_combination_product_id = self.env['price.combination.products'].search([('promotion_id','=',promotion.id),('product_id','=', product_2.id)], limit=1)
            if price_combination_product_id:
                price_combination_product_id.unlink()

        if products_mes3:
            price_combination_product_id = self.env['price.combination.products'].search([('promotion_id','=',promotion.id),('product_id','=', product_3.id)], limit=1)
            if price_combination_product_id:
                price_combination_product_id.unlink()
                
        if products_mes4:
            price_combination_product_id = self.env['price.combination.products'].search([('promotion_id','=',promotion.id),('product_id','=', product_4.id)], limit=1)
            if price_combination_product_id:
                price_combination_product_id.unlink()
                

        if products_mes5:
            price_combination_product_id = self.env['price.combination.products'].search([('promotion_id','=',promotion.id),('product_id','=', product_5.id)], limit=1)
            if price_combination_product_id:
                price_combination_product_id.unlink()
                
        if products_mes6:
            price_combination_product_id = self.env['price.combination.products'].search([('promotion_id','=',promotion.id),('product_id','=', product_6.id)], limit=1)
            if price_combination_product_id:
                price_combination_product_id.unlink()
                
    def delete_mix_and_mathc_comb_with_line(self, line, rows, promotion):
        try:
            products_mes1, product_1 = self.check_product(rows['sku1'])
            products_mes2, product_2 = self.check_product(rows['sku2'])
            products_mes3, product_3 = self.check_product(rows['sku3'])
            products_mes4, product_4 = self.check_product(rows['sku4'])
            products_mes5, product_5 = self.check_product(rows['sku5'])
            products_mes6, product_6 = self.check_product(rows['sku6'])
            products = []
            if products_mes1:
                price_combination_product_id = self.env['price.combination.products'].search([('promotion_id','=',promotion.id),('product_id','=', product_1.id)], limit=1)
                if price_combination_product_id:
                    price_combination_product_id.unlink()

            if products_mes2:
                price_combination_product_id = self.env['price.combination.products'].search([('promotion_id','=',promotion.id),('product_id','=', product_2.id)], limit=1)
                if price_combination_product_id:
                    price_combination_product_id.unlink()

            if products_mes3:
                price_combination_product_id = self.env['price.combination.products'].search([('promotion_id','=',promotion.id),('product_id','=', product_3.id)], limit=1)
                if price_combination_product_id:
                    price_combination_product_id.unlink()
                    
            if products_mes4:
                price_combination_product_id = self.env['price.combination.products'].search([('promotion_id','=',promotion.id),('product_id','=', product_4.id)], limit=1)
                if price_combination_product_id:
                    price_combination_product_id.unlink()
                    

            if products_mes5:
                price_combination_product_id = self.env['price.combination.products'].search([('promotion_id','=',promotion.id),('product_id','=', product_5.id)], limit=1)
                if price_combination_product_id:
                    price_combination_product_id.unlink()
                    
            if products_mes6:
                price_combination_product_id = self.env['price.combination.products'].search([('promotion_id','=',promotion.id),('product_id','=', product_6.id)], limit=1)
                if price_combination_product_id:
                    price_combination_product_id.unlink()
                    
            line.state = "done"
            line.err_msg = "Success"
        except Exception as e:
            line.state = "error"
            line.err_msg = str(e)
    
    def _process_download(self):
        _logger.info("run_process_download")
        # As this function is in a new thread, I need to open a new cursor, because the old one may be closed
        active_id = self.id
        _logger.info('active_id')
        _logger.info(active_id)
        with api.Environment.manage(), self.pool.cursor() as new_cr:
            # new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            # active_id = self.env.context.get('active_id')
            self.state = 'in_progress'
            self.env.cr.commit()
            #Old Method
            #self.env['mix.and.match.comb.file'].generate_file(active_id)
            # New Method
            self.env['mix.and.match.comb.file']._import_data(active_id)
            self.env['mix.and.match.comb.file'].generate_data(active_id)
            # new_cr.commit()

    def import_data(self):
        for row in self:
            row.message_post(body='Start Import')
            self._import_data(row.id)
            row.message_post(body='Finish Import')

    def _import_data(self, id):
        _logger.info("Start Import Data")
        file_id = self.env['mix.and.match.comb.file'].browse(id)
        #file_id.message_post(body='Start Import')
        file_content = base64.b64decode(file_id.file)
        file_content = file_content.decode("utf-8")
        file_lines = file_content.split("\r\n")
        for line in file_lines:
            _logger.info(line)
            rows = self._rows(line)
            if rows['record_flag'] == 'A':
                crud = 'add'
            elif rows['record_flag'] == 'B':
                crud = 'update'
            elif rows['record_flag'] == 'C':
                crud = 'del'
            vals = {
                'mix_and_match_comb_file_id': file_id.id,
                'crud': crud,
                'name': line,
            }
            self.env['mix.and.match.comb.line'].create(vals)
        #file_id.message_post(body='Finish Import')
        _logger.info("Finish Import Data")

    def generate_file(self, id):
        # Example : N5C31990.001
        try:
            mix_and_match_comb_file_id = self.env['mix.and.match.comb.file'].browse(id)
            filename = mix_and_match_comb_file_id.filename
            filename = filename.replace(".","")
            store_code = filename[7:11]
            _logger.info(store_code)

            file_content = base64.b64decode(mix_and_match_comb_file_id.file)
            file_content = file_content.decode("utf-8")
            file_lines = file_content.split("\r\n")

            for line in file_lines:
                _logger.info(str(len(line)))
                rows = self._rows(line)
                _logger.info(rows)
                if rows['mm_type']:
                    store_mes, store = self.check_branch(store_code)
                    if store_mes:
                        promo_no = "{}{}".format(rows['mm_type'], rows['promo_no'])
                        promotion_mes, promotion = self.check_store_promo(promo_no, store)
                        if not promotion_mes:
                            # Promo not found , create new promo
                            result, promotion = self.create_promo(rows, store) #checked                        
                        if promotion:
                            if rows['record_flag'] == 'A':
                                self.create_mix_and_match_comb(rows, promotion) #checked

                            if rows['record_flag'] == 'B':
                                    self.update_mix_and_match_comb(rows, promotion)

                            if rows['record_flag'] == 'C':
                                # promotion_mes, promotion = self.check_mix_and_match_partial(promo_no)                             
                                self.delete_mix_and_mathc_comb(rows, promotion)

                        # if check:
                        #     self.update_mix_and_match_comb(rows, promotion.id, store.id)
                        # else:
                        #     self.create_mix_and_match_comb(rows, store.id)

            mix_and_match_comb_file_id.date_end = datetime.now()
            mix_and_match_comb_file_id.state = 'done'
            self.env.cr.commit()

        except Exception as e:
            _logger.error(e)        
            mix_and_match_comb_file_id.date_end = datetime.now()
            mix_and_match_comb_file_id.state = 'error'
            self.env.cr.commit()
            
    def generate_data(self, id):
        # Example : N5C31990.001
        try:
            mix_and_match_comb_file_id = self.env['mix.and.match.comb.file'].browse(id)
            filename = mix_and_match_comb_file_id.filename
            filename = filename.replace(".","")
            store_code = filename[7:11]
            _logger.info(store_code)
            store_mes, store = self.check_branch(store_code)

            for line in mix_and_match_comb_file_id.mix_and_match_comb_line_ids:
                rows = self._rows(line['name'])
                _logger.info(rows)
                if rows['mm_type']:
                    store_mes, store = self.check_branch(store_code)
                    if store_mes:
                        promo_no = "{}{}".format(rows['mm_type'], rows['promo_no'])
                        promotion_mes, promotion = self.check_store_promo(promo_no, store)
                        if not promotion_mes:
                            # Promo not found , create new promo
                            result, promotion = self.create_promo(rows, store) #checked   
                        else:
                            self.update_promo(rows, promotion)          

                        if promotion:
                            if rows['record_flag'] == 'A':
                                self.create_mix_and_match_comb_with_line(line, rows, promotion) #checked

                            if rows['record_flag'] == 'B':
                                    self.update_mix_and_match_comb_with_line(line, rows, promotion)

                            if rows['record_flag'] == 'C':
                                # promotion_mes, promotion = self.check_mix_and_match_partial(promo_no)                             
                                self.delete_mix_and_mathc_comb_with_line(line, rows, promotion)

                        # if check:
                        #     self.update_mix_and_match_comb(rows, promotion.id, store.id)
                        # else:
                        #     self.create_mix_and_match_comb(rows, store.id)

            mix_and_match_comb_file_id.date_end = datetime.now()
            mix_and_match_comb_file_id.state = 'done'
            self.env.cr.commit()

        except Exception as e:
            _logger.error(e)        
            mix_and_match_comb_file_id.date_end = datetime.now()
            mix_and_match_comb_file_id.state = 'error'
            self.env.cr.commit()

    def cron_process_download(self):     
        #Running Thread
        if self.is_use_thread:
            _logger.info("running thread")
            threaded_download = threading.Thread(target=self._process_download, args=())
            threaded_download.start()    
        else:
            self._process_download()            

    def process_download(self):     
        #Running Thread
        if self.is_use_thread:
            _logger.info("running thread")
            threaded_download = threading.Thread(target=self._process_download, args=())
            threaded_download.start()           
            #threaded_download.join()
            return {'type': 'ir.actions.client', 'tag': 'reload'}                     
        else:
            self._process_download()

    file = fields.Binary('File')
    filename = fields.Char('Filename', size=200)
    date_start = fields.Datetime('Start Date', default=datetime.now(), readonly=1)
    date_end = fields.Datetime('End Date', readonly=1)    
    is_use_thread = fields.Boolean('Use Threading', default=True)
    mix_and_match_comb_line_ids = fields.One2many('mix.and.match.comb.line','mix_and_match_comb_file_id', 'Lines')
    lines_count = fields.Integer('Line Count', compute="get_lines_count")
    download_id = fields.Many2one('pos.interface.download','Download #', ondelete='set null')
    state = fields.Selection([('draft','New'),('in_progress','In Progress'),('done','Finished'),('cancel','Cancel')], 'Status', default='draft')


class MixAndMatchCombinationLine(models.Model):
    _name = 'mix.and.match.comb.line'

    def action_reprocess(self): 
        pass
            
    mix_and_match_comb_file_id = fields.Many2one('mix.and.match.comb.file', 'Product Items File')
    name = fields.Text("Data")
    crud = fields.Selection([
        ('add','Add/Update'),
        ('update','Update'),
        ('del','Delete')
        ],'Type')
    state = fields.Selection([
        ('open','Open'),
        ('progress','Process'),
        ('done','Success'),
        ('error','Error')
        ],'Status', default='open', readonly=True, tracking=True)
    err_msg = fields.Char("Message", size=255)
