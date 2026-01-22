import logging
from datetime import datetime
from odoo.exceptions import Warning, ValidationError
from odoo import models, fields, api, exceptions, _
import threading
import base64

_logger = logging.getLogger(__name__)

class mix_and_match_partial_file(models.Model):
    _name= "mix.and.match.partial.file"
    _rec_name="filename"
    _order = "date_start desc"

    @api.depends('mix_and_match_partial_line_ids')
    def get_lines_count(self):
        for row in self:
            row.lines_count = len(row.mix_and_match_partial_line_ids)

    def action_view_lines(self):
        return {
            'name': _('Lines'),
            'res_model': 'mix.and.match.partial.line',
            'view_mode': 'tree,form',
            'views': [
                (self.env.ref('weha_upload_transpos.view_mix_and_match_partial_line_tree').id, 'tree'),
                (self.env.ref('weha_upload_transpos.view_mix_and_match_partial_line_form').id, 'form'),
                ],
            'type': 'ir.actions.act_window',
            'domain': [('mix_and_match_partial_file_id', 'in', self.ids)],
        }

    def _rows(self, line):
        data = {
            'mm_type': line[0:1].strip(),
            'promo_no' : line[1:13].strip(),
            'sku_no' : line[13:26].strip(),
            'mm_qty' : line[26:34].strip(),
            'mm_start_date' : line[34:42].strip(),
            'mm_end_date' : line[42:50].strip(),
            'mm_start_time' : line[50:54].strip(),
            'mm_end_time' : line[54:58].strip(),
            'mm_fix_foc_qty' : line[58:60].strip(),
            'promo_price' : line[60:77].strip(),
            'promo_disc_name' : line[77:90].strip(),
            'record_flag': line[90:92].strip(),
            'end_of_record': line[92:94].strip()
        }
        return data
    
    #Checked
    def check_store_promo(self, mm_partial_code, store):
        promotion_id = self.env['pos.promotion'].search([('promotion_code','=', mm_partial_code),('branch_ids','in',store.id)], limit=1)
        if promotion_id:        
            return True, promotion_id
        else:
            mes = False
            return mes, ""
    
    def check_mix_and_match_partial_line(self, promotion_type, promotion_id, product_id):
        
        if promotion_type == "buy_x_partial_quantity_get_special_price":
            res = self.env['fixed.price.multi.products'].search([("promotion_id","=", promotion_id), ("product_ids", "in", product_id),], limit=1)
            if res:
                mes = True
                return mes, res
            else:
                mes = False
                return mes, res
            
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
        _logger.info("Check Product")
        products = self.env['product.template'].search([('default_code','=', sku_no)], limit=1)
        if products:
            product_product_id = self.env['product.product'].search([('product_tmpl_id','=', products.id)], limit=1)
            if product_product_id:
                mes = True
                return mes, product_product_id
            else:
                mes = False
                return mes, products
        else:
            mes = False
            return mes, products
    
    def check_branch(self, store_no):
        _logger.info("Check Branch")
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
        
    #Checked
    def create_promo(self, rows, store):
        _logger.info("Promo not found then create new promo for this store")
        start_date = rows['mm_start_date']
        start_date = str(start_date[:4]) + "-" + str(start_date[4:6]).zfill(2) + "-" + str(start_date[6:]).zfill(2)
        end_date = rows['mm_end_date'].replace(" ","")
        end_date = str(end_date[:4]) + "-" + str(end_date[4:6]).zfill(2) + "-" + str(end_date[6:]).zfill(2)
        from_time = int(rows['mm_start_time'][:2])
        to_time = int(rows['mm_end_time'][:2])
        promo_no = "{}{}".format(rows['mm_type'], rows['promo_no'])
        promo_desc = rows['promo_disc_name']
        vals = {
            'active': True,
            'promotion_code': promo_no,
            'promotion_description': promo_desc,
            'branch_ids': [store.id],
            'from_date': start_date,
            'to_date': end_date,
            'from_time': "{}".format(from_time),
            'to_time': "{}".format(to_time),
        }
        if rows['mm_type'] == "Q":
            if int(rows['mm_fix_foc_qty']) == 0:
                vals.update({'promotion_type': "buy_x_quantity_get_special_price",})
            else:
                vals.update({'promotion_type': "buy_x_get_y",})

        if rows['mm_type'] == "P":
            if int(rows['mm_fix_foc_qty']) == 0:
                vals.update({'promotion_type': "buy_x_partial_quantity_get_special_price",})
            else:
                vals.update({'promotion_type': "buy_x_partial_quantity_get_special_price",})

        promotion_id = self.env['pos.promotion'].create(vals)    
        return True, promotion_id

    def update_promo(self, rows, promotion, store):
        _logger.info("Promo  found then update promo for this store")
        start_date = rows['mm_start_date']
        start_date = str(start_date[:4]) + "-" + str(start_date[4:6]).zfill(2) + "-" + str(start_date[6:]).zfill(2)
        end_date = rows['mm_end_date'].replace(" ","")
        end_date = str(end_date[:4]) + "-" + str(end_date[4:6]).zfill(2) + "-" + str(end_date[6:]).zfill(2)
        from_time = int(rows['mm_start_time'][:2])
        to_time = int(rows['mm_end_time'][:2])
        promo_desc = rows['promo_disc_name']
        vals = {
            'active': True,
            'promotion_description': promo_desc,
            'from_date': start_date,
            'to_date': end_date,
            'from_time': "{}".format(from_time),
            'to_time': "{}".format(to_time),
        }
        promotion.write(vals)

    def create_mix_and_match_partial(self, rows, store_id):
        if rows['mm_type']:
            products_mes, products = self.check_product(rows['sku_no'])
            if products_mes:
                start_date = rows['mm_start_date']
                start_date = str(start_date[:4]) + "-" + str(start_date[4:6]).zfill(2) + "-" + str(start_date[6:]).zfill(2)
                end_date = rows['mm_end_date'].replace(" ","")
                end_date = str(end_date[:4]) + "-" + str(end_date[4:6]).zfill(2) + "-" + str(end_date[6:]).zfill(2)
                from_time = int(rows['mm_start_time'][:2])
                to_time = int(rows['mm_end_time'][:2])
                promo_no = "{}{}".format(rows['mm_type'], rows['promo_no'])
                promo_desc = rows['promo_disc_name']
                vals = {
                    'active': True,
                    'promotion_code': promo_no,
                    'promotion_description': promo_desc,
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
                                            'quantity_amt': int(rows['mm_qty']),
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
                                            'quantity': int(rows['mm_qty']),
                                            'product_y_id': products.id,
                                            'quantity_y': int(rows['mm_fix_foc_qty']),
                                        })]
                        })

                if rows['mm_type'] == "P":

                    if int(rows['mm_fix_foc_qty']) == 0:
                        vals.update({
                            'promotion_type': "buy_x_partial_quantity_get_special_price",
                            'pos_partial_quantity_fixed_price_ids': [(0,0, {
                                'product_ids': [products.id],
                                'quantity': int(rows['mm_qty']),
                                'quantity_amt': int(rows['mm_fix_foc_qty']),
                                'fixed_price': rows['promo_price'],
                            })]
                        })
                    else:
                        vals.update({
                            'promotion_type': "buy_x_partial_quantity_get_special_price",
                            'pos_partial_quantity_fixed_price_ids': [(0,0, {
                                'product_ids': [products.id],
                                'quantity': int(rows['mm_qty']),
                                'quantity_amt': int(rows['mm_fix_foc_qty']),
                                'fixed_price': rows['promo_price'],
                            })]
                        })

                _logger.info("CREATE PROMOTION")
                _logger.info(vals)
                self.env['pos.promotion'].create(vals)

    def update_mix_and_match_partial(self, rows, mm_partial_id, promotion_type, product_id, store_id):
        products_mes, products = self.check_product(rows['sku_no'])
        if products_mes:
            res = self.env['pos.promotion'].search([('id','=', mm_partial_id)], limit=1)
            # res.promotion_description(rows['promo_disc_name'])
            promo_store_mes = self.check_promotion_store(mm_partial_id, store_id)
            vals = {}
            if promo_store_mes != True:
                vals.update({'branch_ids': [(4, store_id)]})

            if rows['mm_type'] == "Q":
                if int(rows['mm_fix_foc_qty']) == 0:
                    # 'promotion_type': "buy_x_quantity_get_special_price",
                    vals.update({
                        'pos_quantity_fixed_price_ids': [(0,0, {
                                        'product_id': products.id,
                                        'quantity_amt': int(rows['mm_qty']),
                                        'fixed_price': rows['promo_price'],
                                    })]
                    })
                else:
                    # 'promotion_type': "buy_x_get_y",
                    vals.update({
                        'pos_condition_ids': [(0,0, {
                                        'product_x_id': products.id,
                                        'operator': "greater_than_or_eql",
                                        'quantity': int(rows['mm_qty']),
                                        'product_y_id': products.id,
                                        'quantity_y': int(rows['mm_fix_foc_qty']),
                                    })]
                    })

            _logger.info("UPDATE PROMOTION")
            # _logger.info(vals)
            res.write(vals)
            if rows['mm_type'] == "P":
                # buy_x_partial_quantity_get_special_price
                for line in res.pos_partial_quantity_fixed_price_ids:
                    line.product_ids = [(4, products.id)]

    def delete_mix_and_match_partial(self, rows, promotion, products):
        try:
            if rows['mm_type'] == "Q":            
                if int(rows['mm_fix_foc_qty']) == 0:
                    pos_quantity_fixed_price_id = self.env['quantity.fixed.price'].search([('pos_promotion_id','=',promotion.id),('product_id','=', products.id)])
                    pos_quantity_fixed_price_id.unlink_all()                                                                                            
                else:
                    pos_conditions_id = self.env['pos.conditions'].search([('pos_promotion_rel','=',promotion.id),('product_x_id','=', products.id)])
                    pos_conditions_id.unlink_all()

            _logger.info("UPDATE PROMOTION")
            if rows['mm_type'] == "P":
                # buy_x_partial_quantity_get_special_price
                for line in promotion.pos_partial_quantity_fixed_price_ids:
                    line.product_ids = [(3, products.id)]
        except Exception as e:
            line.state = "error"
            line.err_msg = str(e)

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
                            else:
                                promotion.pos_partial_quantity_fixed_price_ids[0].product_ids = [(4, products.id)]
                            
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
                            else:
                                promotion.pos_partial_quantity_fixed_price_ids[0].product_ids = [(4, products.id)]               
                    # _logger.info(vals)
                    # self.env['pos.promotion'].create(vals)
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

        except Exception as e:
            line.state = "error"        
            line.err_msg = str(e)

    def delete_mix_and_match_partial_with_line(self, line, rows, promotion, products):
        try:
            if rows['mm_type'] == "Q":            
                if int(rows['mm_fix_foc_qty']) == 0:
                    pos_quantity_fixed_price_id = self.env['quantity.fixed.price'].search([('pos_promotion_id','=',promotion.id),('product_id','=', products.id)])
                    pos_quantity_fixed_price_id.unlink()      
                    line.stage = "done"
                    line.err_msg = "Success"
                                                                                      
                else:
                    pos_conditions_id = self.env['pos.conditions'].search([('pos_promotion_rel','=',promotion.id),('product_x_id','=', products.id)])
                    pos_conditions_id.unlink()
                    line.stage = "done"
                    line.err_msg = "Success"


            _logger.info("UPDATE PROMOTION")
            if rows['mm_type'] == "P":
                # buy_x_partial_quantity_get_special_price
                if len(promotion.pos_partial_quantity_fixed_price_ids) > 0:
                    pos_partial_quantity_fixed_price_id = promotion.pos_partial_quantity_fixed_price_ids
                    pos_partial_quantity_fixed_price_id.product_ids =  [(3, products.id)]
                    line.state = "done"
                    line.err_msg = "Success"
                else:
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
            # Old Method
            # self.env['mix.and.match.partial.file'].generate_file(active_id)  
            # New Method
            self.env['mix.and.match.partial.file']._import_data(active_id)          
            self.env['mix.and.match.partial.file'].generate_data(active_id)  
     
    def import_data(self):
        for row in self:
            row.message_post(body='Start Import')
            self._import_data(row.id)
            row.message_post(body='Finish Import')

    def _import_data(self, id):
        _logger.info("Start Import Data")
        file_id = self.env['mix.and.match.partial.file'].browse(id)
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
                'mix_and_match_partial_file_id': file_id.id,
                'crud': crud,
                'name': line,
            }
            self.env['mix.and.match.partial.line'].create(vals)
        #file_id.message_post(body='Finish Import')
        _logger.info("Finish Import Data")

    def generate_file(self, id):
        _logger.info("generate_file")
        # Example : M5C31990.001
        mix_and_match_partial_file_id = self.env['mix.and.match.partial.file'].browse(id)
        try:
            filename = mix_and_match_partial_file_id.filename
            filename = filename.replace(".","")        
            store_code = filename[7:11]
            _logger.info("Process Store : " + store_code)

            file_content = base64.b64decode(mix_and_match_partial_file_id.file)
            file_content = file_content.decode("utf-8")
            file_lines = file_content.split("\r\n")

            for line in file_lines:
                rows = self._rows(line)                
                # Check Store is ready?
                store_mes, store = self.check_branch(store_code)
                if store_mes:
                    # Check Product is ready?   
                    _logger.info(store.id)                 
                    products_mes, products = self.check_product(rows['sku_no'])
                    if products_mes:
                        # Check Promotion is ready?
                        promo_no = "{}{}".format(rows['mm_type'], rows['promo_no'])
                        promotion_mes, promotion = self.check_store_promo(promo_no, store) #checked
                        if not promotion_mes:
                            # Promo not found , create new promo
                            result, promotion = self.create_promo(rows, store) #checked
                        if promotion:
                            if rows['record_flag'] == 'A':
                                self.create_mix_and_match_partial(rows, promotion) #checked

                            if rows['record_flag'] == 'B':
                                 self.update_mix_and_match_partial(rows, promotion, products, store.id)

                            if rows['record_flag'] == 'C':
                                # promotion_mes, promotion = self.check_mix_and_match_partial(promo_no)                             
                                self.delete_mix_and_match_partial(rows, promotion, products)

                        # if promotion_mes:
                        #     self.update_mix_and_match_partial(rows, promotion.id, promotion.promotion_type, products.id, store.id)
                        # else:
                        #     self.create_mix_and_match_partial(rows, store.id)

            mix_and_match_partial_file_id.date_end = datetime.now()
            mix_and_match_partial_file_id.state = 'done'
            self.env.cr.commit()
        except Exception as e:
            _logger.error(e)
            mix_and_match_partial_file_id.date_end = datetime.now()
            mix_and_match_partial_file_id.state = 'error'
            self.env.cr.commit()
            
    def generate_data(self, id):
        _logger.info("generate_data")
        # Example : M5C31990.001
        mix_and_match_partial_file_id = self.env['mix.and.match.partial.file'].browse(id)
        try:
            filename = mix_and_match_partial_file_id.filename
            filename = filename.replace(".","")        
            store_code = filename[7:11]
            _logger.info("Process Store : " + store_code)
            store_mes, store = self.check_branch(store_code)
            if store_mes:
                _logger.info(store.id)
                for line in mix_and_match_partial_file_id.mix_and_match_partial_line_ids:                    
                    rows = self._rows(line['name'])         
                    products_mes, products = self.check_product(rows['sku_no'])
                    if products_mes:
                        # Check Promotion is ready?
                        promo_no = "{}{}".format(rows['mm_type'], rows['promo_no'])
                        promotion_mes, promotion = self.check_store_promo(promo_no, store) #checked
                        if not promotion_mes:
                            # Promo not found , create new promo
                            result, promotion = self.create_promo(rows, store) #checked
                        else:
                            self.update_promo(rows, promotion, store)
                        if promotion:
                            if rows['record_flag'] == 'A':
                                self.create_mix_and_match_partial_with_line(line, rows, promotion) #checked
                            if rows['record_flag'] == 'B':
                                self.update_mix_and_match_partial_with_line(line, rows, promotion, products, store)
                            if rows['record_flag'] == 'C':
                                self.delete_mix_and_match_partial_with_line(line, rows, promotion, products)
                        else:
                            line.state = "error"
                            line.err_msg = "Promotion error"
                    else:
                        line.state = "error"
                        line.err_msg = "Product not found"
            else:
                pass                 

            mix_and_match_partial_file_id.date_end = datetime.now()
            mix_and_match_partial_file_id.state = 'done'
            self.env.cr.commit()
        except Exception as e:
            _logger.error(e)
            # mix_and_match_partial_file_id.date_end = datetime.now()
            # mix_and_match_partial_file_id.state = 'done'
            # self.env.cr.commit()
            
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
            # threaded_download.join()
            return {'type': 'ir.actions.client', 'tag': 'reload'}                     
        else:
            self._process_download()

    file = fields.Binary('File')
    filename = fields.Char('Filename', size=200)
    date_start = fields.Datetime('Start Date', default=datetime.now(), readonly=1)
    date_end = fields.Datetime('End Date', readonly=1)
    is_use_thread = fields.Boolean('Use Threading', default=True)
    download_id = fields.Many2one('pos.interface.download','Download #', ondelete='set null')
    mix_and_match_partial_line_ids = fields.One2many('mix.and.match.partial.line','mix_and_match_partial_file_id', 'Lines')
    lines_count = fields.Integer('Line Count', compute="get_lines_count")
    state = fields.Selection([('draft','New'),('in_progress','In Progress'),('done','Finished'),('cancel','Cancel')], 'Status', default='draft')

class MixAndMatchPartialLine(models.Model):
    _name = 'mix.and.match.partial.line'

    def action_reprocess(self): 
        pass
            
    mix_and_match_partial_file_id = fields.Many2one('mix.and.match.partial.file', 'Product Items File')
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
