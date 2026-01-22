from odoo import models, fields, api, _ 
from datetime import datetime, date, timedelta
import time

import logging
_logger = logging.getLogger(__name__)


class PosOrderLineReport(models.AbstractModel):
    _name = 'report.weha_smart_pos_aeon_pos_report.pos_order_line_report'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'POS Order Line Report'

    def getData(self, start_date, end_date, branch_id):
        strSQL="""SELECT 
                b.pos_reference, b.date_order, j.code as line, h.code as division, g.code as group, f.code as department, d.name as name, a.qty as sold_qty, a.price_subtotal_incl as sales_amount 
                FROM pos_order_line a
                LEFT JOIN pos_order b ON a.order_id = b.id
                LEFT JOIN product_product c ON a.product_id = c.id
                LEFT JOIN product_template d ON c.product_tmpl_id = d.id
                LEFT JOIN res_branch e ON b.branch_id = e.id
                LEFT JOIN product_category f ON d.categ_id = f.id
                LEFT JOIN res_department g ON f.dept_id = g.id
                LEFT JOIN res_division h ON g.division_id = h.id
                LEFT JOIN res_line j ON h.line_id = j.id
                WHERE b.date_order BETWEEN '{}' AND '{}' AND e.id={}
        """.format(start_date, end_date, branch_id.id)        
        _logger.info(strSQL)
        self.env.cr.execute(strSQL)
        rows = self.env.cr.fetchall()
        datas = []
        for row in rows:
            vals = {
                'pos_reference': row[0],
                'date_order': row[1],
                'line': row[2],
                'division': row[3],
                'group': row[4],
                'department': row[5],
                'product': row[6]['en_US'],
                'sold_qty': row[7],
                'sales_amount': row[8],                
            }
            datas.append(vals)    
            _logger.info(vals)
        return datas
    
    def generate_xlsx_report(self, workbook, data, obj):
        # _logger.info(data)     
        _logger.info(obj.start_date)
        _logger.info(obj.end_date)  
        if time.tzname[0] == 'WIB':
            start_date = obj.start_date - timedelta(hours=7) 
            end_date = obj.end_date - timedelta(hours=7) 
        else:
            start_date = obj.start_date 
            end_date = obj.end_date 

        lines = self.getData(start_date,end_date, obj.branch_id) 
        row = 0
        sheet = workbook.add_worksheet('POS Order Line Report')
        format_date_time = workbook.add_format({'num_format': 'dd-mm-yyyy hh:mm:ss'})    
        sheet.write(row,0, 'Receipt No')
        sheet.write(row,1, 'Date Time')
        sheet.write(row,2, 'Line')
        sheet.write(row,3, 'Division')
        sheet.write(row,4, 'Group')
        sheet.write(row,5, 'Department')
        sheet.write(row,6, 'Product')
        sheet.write(row,7, 'Sold Qty')
        sheet.write(row,8, 'Sales Amount')
        row+=1
        for line in lines:         
            sheet.write(row,0, line['pos_reference'])
            sheet.write(row,1, line['date_order'], format_date_time)
            sheet.write(row,2, line['line'])
            sheet.write(row,3, line['division'])
            sheet.write(row,4, line['group'])
            sheet.write(row,5, line['department'])
            sheet.write(row,6, line['product'])
            sheet.write(row,7, line['sold_qty'])
            sheet.write(row,8, line['sales_amount'])
            row+=1