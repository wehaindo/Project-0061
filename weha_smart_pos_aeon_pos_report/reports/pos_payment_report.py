from odoo import models, fields, api, _ 


import logging
_logger = logging.getLogger(__name__)


class PosPaymentReport(models.AbstractModel):
    _name = 'report.weha_smart_pos_aeon_pos_report.pos_payment_report'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'POS Payment Report'

    def getData(self, branch_id, start_date, end_date):
        strSQL = """
                    select e.code, a.payment_date, b.pos_reference, c.name, 
                    a.amount, a.pan, a.approval_code, c.description, a.merchant_id, 
                    a.terminal_id, c.use_payment_terminal 
                    from pos_payment a 
                    left join pos_order b on a.pos_order_id = b.id 
                    left join pos_payment_method  c on a.payment_method_id = c.id 
                    left join pos_session d on b.session_id = d.id 
                    left join pos_config e on d.config_id = e.id where a.branch_id={} and b.date_order between '{}' and '{}'
        """.format(branch_id.id, start_date, end_date)
        self.env.cr.execute(strSQL)
        rows = self.env.cr.fetchall()
        datas = []
        for row in rows:
            vals = {
                'code': row[0],
                'payment_date': row[1],
                'pos_reference': row[2],
                'payment_method': row[3],
                'amount': row[4],
                'pan': row[5],
                'approval_code': row[6],
                'description': row[7],
                'merchant_id': row[8],
                'terminal_id': row[9],
                'use_payment_terminal': row[10] 
            }
            datas.append(vals)    
        return datas
    
    def generate_xlsx_report(self, workbook, data, obj):
        # _logger.info(data)     
        _logger.info(obj.start_date)
        _logger.info(obj.end_date)  
        lines = self.getData(obj.branch_id, obj.start_date,obj.end_date) 
        row = 0
        sheet = workbook.add_worksheet('POS Payment Report')
        format_date_time = workbook.add_format({'num_format': 'dd-mm-yyyy hh:mm:ss'})    
        sheet.write(row,0, 'Code')
        sheet.write(row,1, 'Payment Date')
        sheet.write(row,2, 'POS Reference')
        sheet.write(row,3, 'Payment Method')
        sheet.write(row,4, 'Amount')
        sheet.write(row,5, 'Card Number')
        sheet.write(row,6, 'Approval Code')
        sheet.write(row,7, 'Description')
        sheet.write(row,8, 'Merchant ID')
        sheet.write(row,9, 'Terminal ID')
        sheet.write(row,10, 'Payment Terminal')
        row+=1
        for line in lines:         
            sheet.write(row,0, line['code'])
            sheet.write(row,1, line['payment_date'], format_date_time)
            sheet.write(row,2, line['pos_reference'])
            sheet.write(row,3, line['payment_method']['en_US'])
            sheet.write(row,4, str(line['amount']))
            sheet.write(row,5, line['pan'])
            sheet.write(row,6, line['approval_code'])
            sheet.write(row,7, line['description'])
            sheet.write(row,8, line['merchant_id'])
            sheet.write(row,9, line['terminal_id'])
            sheet.write(row,10, line['use_payment_terminal'])
            row+=1