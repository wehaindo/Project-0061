from odoo import models, fields, api, _ 
from datetime import datetime, date, timedelta

import logging
_logger = logging.getLogger(__name__)


class ProductTemplateReport(models.AbstractModel):
    _name = 'report.weha_smart_pos_aeon_pos_report.product_template_report'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'POS Product Template Report'

    def get_promo_price(self, store_id, product_template_id):
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

    def get_member_promo_price(self, store_id, product_template_id):
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
            promo_price = self.get_promo_price(store_id, product_template_id)
            if promo_price:
                vals.update({
                    'pdc_prc_no': promo_price[0],
                    'pdc_start_date': promo_price[1],
                    'pdc_end_date': promo_price[2],
                    'promotion_price': promo_price[3],                    
                })       
            member_promo_price = self.get_member_promo_price(store_id, product_template_id)
            if member_promo_price:
                vals.update({
                    'pdcm_prc_no': promo_price[0],
                    'pdcm_start_date': promo_price[1],
                    'pdcm_end_date': promo_price[2],
                    'member_promotion_price': promo_price[3],                    
                })            
            datas.append(vals)        
        return datas
    
    def generate_xlsx_report(self, workbook, data, obj):
        # _logger.info(data)     
        lines = self.getData(obj.store_id) 
        row = 0
        sheet = workbook.add_worksheet('POS Payment Report')
        format_date_time = workbook.add_format({'num_format': 'dd-mm-yyyy hh:mm:ss'})    
        sheet.write(row,0, 'Store')
        sheet.write(row,1, 'Line')
        sheet.write(row,2, 'Dept')
        sheet.write(row,3, 'Short SKU')
        sheet.write(row,4, 'Barcode')
        sheet.write(row,7, 'Item Desc')
        sheet.write(row,8, 'Normal Price')
        sheet.write(row,9, 'Price Change #')
        sheet.write(row,10, 'Start Date')
        sheet.write(row,11, 'End Date')
        sheet.write(row,12, 'Promotion Price')
        sheet.write(row,13, 'Price Change #')
        sheet.write(row,14, 'Start Date')
        sheet.write(row,15, 'End Date')        
        sheet.write(row,16, 'Member Promotion Price')
        sheet.write(row,17, 'Group Price Change')
        sheet.write(row,18, 'Member Group Price Change')
        sheet.write(row,19, 'Mix and Match')
        row+=1
        for line in lines:         
            sheet.write(row,0, line['store'])
            sheet.write(row,1, line['line'])
            sheet.write(row,2, line['dept'])
            sheet.write(row,3, line['short_sku'])
            sheet.write(row,4, line['barcode_1'])
            sheet.write(row,5, line['barcode_2'])
            sheet.write(row,6, line['barcode_3'])
            sheet.write(row,7, line['item_desc'])
            sheet.write(row,8, line['normal_price'])
            sheet.write(row,9, line['pdc_prc_no'])
            sheet.write(row,10, line['pdc_start_date'])
            sheet.write(row,11, line['pdc_end_date'])
            sheet.write(row,12, line['promotion_price'])
            sheet.write(row,13, line['pdcm_prc_no'])
            sheet.write(row,14, line['pdcm_start_date'])
            sheet.write(row,15, line['pdcm_end_date'])
            sheet.write(row,16, line['member_promotion_price'])
            sheet.write(row,17, line['group_price_change'])
            sheet.write(row,18, line['member_group_price_change'])
            sheet.write(row,19, line['mix_and_match'])
            row+=1