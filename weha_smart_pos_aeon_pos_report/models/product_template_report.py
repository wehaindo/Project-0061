from odoo import models, fields, api, _ 
from datetime import datetime
import threading
import base64
import logging
import io
import xlsxwriter



_logger = logging.getLogger(__name__)


class AeonProductTemplateReport(models.Model):    
    _name = 'aeon.product.template.report'

    def _process_report(self):
        _logger.info("run_process_report")
        active_id = self.id
        with api.Environment.manage(), self.pool.cursor() as new_cr:
            # new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            self.state = 'in_progress'
            self.env.cr.commit()
            self.env['aeon.product.template.report'].generate_report(active_id)

    def _get_promo_price(self, store_id, product_template_id):
        domain = [
            ('price_type','=','PDC'),
            ('branch_id','=', store_id.id)                      
        ]
        product_pricelist_id = self.env['product.pricelist'].search(domain, limit=1)
        str_current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        strSQL="""
            SELECT prc_no, date_start, date_end, fixed_price FROM product_pricelist_item a
            LEFT JOIN product_template b ON a.product_tmpl_id = b.id
            WHERE pricelist_id={} AND a.product_tmpl_id={} AND date_start <= '{}' AND date_end >= '{}' limit 1          
        """.format(product_pricelist_id.id, product_template_id.id, str_current_date, str_current_date)
        _logger.info(strSQL)
        self.env.cr.execute(strSQL)
        product_pricelist_item_row = self.env.cr.fetchone()
        _logger.info(product_pricelist_item_row)
        return product_pricelist_item_row
        
        # if product_pricelist_id:
        #     domain = [
        #         ('pricelist_id','=', product_pricelist_id.id),
        #         ('product_tmpl_id','=', product_template_id.id),
        #         # ('date_start','<= ',datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        #         # ('date_end','>=',datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        #     ]
        #     product_pricelist_item_id = self.env['product.pricelist.item'].search(domain, limit=1)
        #     return product_pricelist_item_id        
        # return False

    def _get_member_promo_price(self, store_id, product_template_id):
        domain = [
            ('price_type','=','PDCM'),
            ('branch_id','=', store_id.id)                      
        ]
        product_pricelist_id = self.env['product.pricelist'].search(domain, limit=1)
        str_current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        strSQL="""
            SELECT date_start, date_end, fixed_price FROM product_pricelist_item a
            LEFT JOIN product_template b ON a.product_tmpl_id = b.id
            WHERE pricelist_id={} AND a.product_tmpl_id={} AND date_start <= '{}' AND date_end >= '{}' limit 1          
        """.format(product_pricelist_id.id, product_template_id.id, str_current_date, str_current_date)
        _logger.info(strSQL)
        self.env.cr.execute(strSQL)
        product_pricelist_item_row = self.env.cr.fetchone()
        _logger.info(product_pricelist_item_row)
        return product_pricelist_item_row

    def getData(self, store_id):
        domain = [('branch_ids','in',[store_id.id])]    
        product_template_ids = self.env['product.template'].search(domain, order="line_id asc, dept_id asc, name asc")
        datas = []
        for product_template_id in product_template_ids:            
            vals = {
                'store': store_id.code,
                'line': product_template_id.line_id.code,
                'dept': product_template_id.dept_id.code,
                'short_sku': product_template_id.default_code,
                'barcode_1': product_template_id.barcode,
                'barcode_2': '',
                'barcode_3': '',
                'item_desc': product_template_id.name,
                'normal_price': product_template_id.list_price,
                'pdc_prc_no': '',            
                'pdc_start_date': '',
                'pdc_end_date': '',
                'promotion_price': 0,
                'pdcm_prc_no': '',
                'pdcm_start_date': '',
                'pdcm_end_date': '',
                'member_promotion_price': 0,
                'group_price_change': 0,
                'member_group_price_change': 0,
                'mix_and_match': 0,
            } 
            promo_price = self._get_promo_price(store_id, product_template_id)
            if promo_price:
                vals.update({
                    'pdc_prc_no': promo_price[0],
                    'pdc_start_date': promo_price[1],
                    'pdc_end_date': promo_price[2],
                    'promotion_price': promo_price[3],                    
                })       
            member_promo_price = self._get_member_promo_price(store_id, product_template_id)
            if member_promo_price:
                vals.update({
                    'pdcm_prc_no': promo_price[0],
                    'pdcm_start_date': promo_price[1],
                    'pdcm_end_date': promo_price[2],
                    'member_promotion_price': promo_price[3],                    
                })            
            datas.append(vals)        
        return datas

    def generate_report(self, id):
        aeon_product_template_report_id = self.env['aeon.product.template.report'].browse(id)
        lines = self.getData(aeon_product_template_report_id.store_id.id) 
        row = 0
        _logger.info("Line Row  : " + str(len(lines)))

    def action_process(self):
        threaded_download = threading.Thread(target=self._process_report, args=())
        threaded_download.start()   

    store_id = fields.Many2one('res.branch', 'Store', required=True)
    filename = fields.Char('Filename')
    filedata = fields.Binary('File')
    date_start = fields.Datetime('Start Date', default=datetime.now())
    end_date = fields.Datetime('End Date')
    state = fields.Selection([('open','Open'),('inprogres','In Progres'),('done','Finish'),('error','Error')], "status", default='open')

