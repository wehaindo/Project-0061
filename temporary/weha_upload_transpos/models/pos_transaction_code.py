from odoo import _, api, fields, models
from datetime import datetime, timedelta, date
from dateutil.relativedelta import *
from io import StringIO
import io
import base64

import logging

_logger = logging.getLogger(__name__)

class GenerateTransPOS(models.Model):
    _name = "pos.trans.code"
    _description = "POS Transaction Code"
    _rec_name="master_code_filename"
    _order = 'date DESC'

    def file_name(self, lastnumb):
        date_time = datetime.now()
        # sequence number
        number_RR = hex(lastnumb)
        if len(number_RR) > 3:
            RR = number_RR[2:]
        else:
            RR = "0"+number_RR[2:]

        Y = date_time.strftime("%Y")[3:]
        Month = date_time.strftime("%m")
        Month_Hex = hex(int(Month))
        M = Month_Hex[2:]
        D = date_time.strftime("%d")
        filename = "RH{}{}{}{}".format(Y, M, D, RR.upper())

        return filename
    
    def _validate_row(self, starthour, endhour, branch_id, branch_code, hour):
        sqlrow="""SELECT count(a.id) as transaction_count
                FROM pos_order_line a
                LEFT JOIN pos_order b ON a.order_id = b.id
                LEFT JOIN product_product c ON a.product_id = c.id
                LEFT JOIN product_template d ON c.product_tmpl_id = d.id
                LEFT JOIN res_branch e ON b.branch_id = e.id
                WHERE a.create_date BETWEEN '{}' AND '{}' AND e.id={}""".format(starthour, endhour, branch_id)
        self.env.cr.execute(sqlrow)
        lines = self.env.cr.dictfetchall()
        master_row = []
        for line in lines:
            line_code = str(branch_code).ljust(10, ' ')
            transaction_count = str(line["transaction_count"]).rjust(7, ' ')
            master = f'{branch_code}STR{line_code}{hour}{transaction_count}'
            master_row.append(master)

        master_row_join = '\n'.join(master_row)
        return master_row_join

    def _validate_line(self, starthour, endhour, branch_id, branch_code, hour):
        sqlline="""SELECT 
                d.line_id, f.code, count(d.default_code) as customer_count
                FROM pos_order_line a
                LEFT JOIN pos_order b ON a.order_id = b.id
                LEFT JOIN product_product c ON a.product_id = c.id
                LEFT JOIN product_template d ON c.product_tmpl_id = d.id
                LEFT JOIN res_branch e ON b.branch_id = e.id
                LEFT JOIN res_line f ON d.line_id = f.id
                WHERE a.create_date BETWEEN '{}' AND '{}' AND e.id={}
                GROUP BY d.line_id, f.code""".format(starthour, endhour, branch_id)
        self.env.cr.execute(sqlline)
        lines = self.env.cr.dictfetchall()
        master_line = []
        for line in lines:
            line_code = str(line["code"]).ljust(10, ' ')
            customer_count = str(line["customer_count"]).rjust(7, ' ')
            # master_line = "{}DPT{}       {}       {}\n".format(branch_code, line['code'], hour, line['customer_count'])
            master = f'{branch_code}DPT{line_code}{hour}{customer_count}'
            master_line.append(master)

        master_line_join = '\n'.join(master_line)
        return master_line_join
    
    def _validate_division(self, starthour, endhour, branch_id, branch_code, hour):
        sqldivision="""SELECT 
                d.division_id, f.code, count(d.default_code) as customer_count
                FROM pos_order_line a
                LEFT JOIN pos_order b ON a.order_id = b.id
                LEFT JOIN product_product c ON a.product_id = c.id
                LEFT JOIN product_template d ON c.product_tmpl_id = d.id
                LEFT JOIN res_branch e ON b.branch_id = e.id
                LEFT JOIN res_division f ON d.division_id = f.id
                WHERE a.create_date BETWEEN '{}' AND '{}' AND e.id={}
                GROUP BY d.division_id, f.code""".format(starthour, endhour, branch_id)
        self.env.cr.execute(sqldivision)
        divisions = self.env.cr.dictfetchall()
        master_div = []
        for div in divisions:
            div_code = str(div["code"]).ljust(10, ' ')
            customer_count = str(div["customer_count"]).rjust(7, ' ')
            # master_line = "{}DPT{}       {}       {}\n".format(branch_code, line['code'], hour, line['customer_count'])
            master = f'{branch_code}SEC{div_code}{hour}{customer_count}'
            master_div.append(master)

        master_division_join = '\n'.join(master_div)
        return master_division_join

    def _validate_group(self, starthour, endhour, branch_id, branch_code, hour):
        sqlgroup="""SELECT 
                d.group_id, f.code, count(d.default_code) as customer_count
                FROM pos_order_line a
                LEFT JOIN pos_order b ON a.order_id = b.id
                LEFT JOIN product_product c ON a.product_id = c.id
                LEFT JOIN product_template d ON c.product_tmpl_id = d.id
                LEFT JOIN res_branch e ON b.branch_id = e.id
                LEFT JOIN res_group f ON d.group_id = f.id
                WHERE a.create_date BETWEEN '{}' AND '{}' AND e.id={}
                GROUP BY d.group_id, f.code""".format(starthour, endhour, branch_id)
        self.env.cr.execute(sqlgroup)
        groups = self.env.cr.dictfetchall()
        master_group = []
        for group in groups:
            group_code = str(group["code"]).ljust(10, ' ')
            customer_count = str(group["customer_count"]).rjust(7, ' ')
            # master_line = "{}DPT{}       {}       {}\n".format(branch_code, line['code'], hour, line['customer_count'])
            master = f'{branch_code}TYP{group_code}{hour}{customer_count}'
            master_group.append(master)

        master_group_join = '\n'.join(master_group)
        return master_group_join

    def _validate_dept(self, starthour, endhour, branch_id, branch_code, hour):
        sqlline="""SELECT 
                d.dept_id, f.code, count(d.default_code) as customer_count
                FROM pos_order_line a
                LEFT JOIN pos_order b ON a.order_id = b.id
                LEFT JOIN product_product c ON a.product_id = c.id
                LEFT JOIN product_template d ON c.product_tmpl_id = d.id
                LEFT JOIN res_branch e ON b.branch_id = e.id
                LEFT JOIN res_department f ON d.dept_id = f.id
                WHERE a.create_date BETWEEN '{}' AND '{}' AND e.id={}
                GROUP BY d.dept_id, f.code""".format(starthour, endhour, branch_id)
        self.env.cr.execute(sqlline)
        depts = self.env.cr.dictfetchall()
        master_dept = []
        for dept in depts:
            dept_code = str(dept["code"]).ljust(10, ' ')
            customer_count = str(dept["customer_count"]).rjust(7, ' ')
            # master_line = "{}DPT{}       {}       {}\n".format(branch_code, line['code'], hour, line['customer_count'])
            master = f'{branch_code}ART{dept_code}{hour}{customer_count}'
            master_dept.append(master)

        master_dept_join = '\n'.join(master_dept)
        return master_dept_join

    def get_transpos(self):
        check_hour = {
            "9": ["08:30:00","09:30:00"], "10": ["09:30:00","10:30:00"], "11": ["10:30:00","11:30:00"], "12": ["11:30:00","12:30:00"], "13": ["12:30:00","13:30:00"],
            "14": ["13:30:00","14:30:00"], "15": ["14:30:00","15:30:00"], "16": ["15:30:00","16:30:00"], "17": ["16:30:00","17:30:00"], "18": ["17:30:00","18:30:00"],
            "19": ["18:30:00","19:30:00"], "20": ["19:30:00","20:30:00"],
        }

        date_time = datetime.now() + relativedelta(hours=7) # example : datetime(2023,6,25,14,10,00)
        time_hour = date_time.strftime("%H:%M:%S")
        time_hour_no = int(time_hour[:2])

        # _logger.info(trans_codes)
        
        if check_hour.get(str(time_hour_no)) != None:
            
            hour = time_hour.replace(':','')
            dis = check_hour[str(time_hour_no)][1].replace(':','')

            if hour >= dis:

                str_start_date = str(date_time.year)+ "-" + str(date_time.month).zfill(2) + "-" + str(date_time.day).zfill(2) + " " + check_hour[str(time_hour_no)][0]
                starthour = datetime.strptime(str_start_date, "%Y-%m-%d %H:%M:%S") - relativedelta(hours=7)

                str_end_date = str(date_time.year) + "-" + str(date_time.month).zfill(2) + "-" + str(date_time.day).zfill(2) + " " + check_hour[str(time_hour_no)][1]
                endhour = datetime.strptime(str_end_date, "%Y-%m-%d %H:%M:%S") - relativedelta(hours=7)
                _logger.info("DATE")
                _logger.info(str(starthour))
                _logger.info(str(endhour))
            
                sqlgroup="""SELECT branch_id FROM pos_order_line
                    WHERE create_date BETWEEN '{}' AND '{}'
                    GROUP BY branch_id""".format(starthour, endhour)
                self.env.cr.execute(sqlgroup)
                groups = self.env.cr.dictfetchall()
                _logger.info(str(groups))
                if len(groups) > 0:
                    for group in groups:
                        _logger.info("START STRING-IO")
                        output = StringIO()
                        branch_code = ""
                        sql_count="""SELECT
                            a.branch_id, e.code as branch_code, count(d.default_code) as customer_count, d.default_code
                            FROM pos_order_line a
                            LEFT JOIN pos_order b ON a.order_id = b.id
                            LEFT JOIN product_product c ON a.product_id = c.id
                            LEFT JOIN product_template d ON c.product_tmpl_id = d.id
                            LEFT JOIN res_branch e ON b.branch_id = e.id
                            WHERE a.create_date BETWEEN '{}' AND '{}' AND a.branch_id={}
                            GROUP BY a.branch_id, e.code, d.default_code""".format(starthour, endhour, group['branch_id'])
                        self.env.cr.execute(sql_count)
                        orders = self.env.cr.dictfetchall()
                        _logger.info(orders)
                        for order in orders:
                            _logger.info("ORDER BY STORE")
                            branch_code = order['branch_code'].zfill(4)
                            _logger.info(str(branch_code))
                            sql="""SELECT
                                e.code, d.default_code, TO_CHAR(a.create_date, 'YYYY-MM-DD HH:MM:SS') as create_date, a.qty, a.price_subtotal, b.partner_id, a.price_subtotal_incl
                                FROM pos_order_line a
                                LEFT JOIN pos_order b ON a.order_id = b.id
                                LEFT JOIN product_product c ON a.product_id = c.id
                                LEFT JOIN product_template d ON c.product_tmpl_id = d.id
                                LEFT JOIN res_branch e ON b.branch_id = e.id
                                WHERE a.create_date BETWEEN '{}' AND '{}' AND d.default_code='{}' AND a.branch_id={}""".format(starthour, endhour, order['default_code'], order['branch_id'])
                            # WHERE a.create_date BETWEEN '{}' AND '{}'   .format(start_hour, next_hour)
                            self.env.cr.execute(sql)
                            lines = self.env.cr.dictfetchall()
                            for line in lines:
                                date = str(line['create_date'])
                                # _logger.info(str(date))
                                # date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                                # hours = date.strftime("%H%M")
                                qty = str(int(line['qty'])).zfill(10)
                                price_subtotal = str(int(line['price_subtotal'])).zfill(22)
                                price_subtotal_incl = str(int(line['price_subtotal_incl'])).zfill(22)
                                master_code = "{}{}{}{}{}{}{}\n".format(line['code'].zfill(4), line['default_code'].ljust(13, ' '), 
                                                                    dis[:4], qty, price_subtotal_incl, str(order['customer_count']).rjust(6, ' '), price_subtotal)
                                
                                output.write(master_code)
                                _logger.info(master_code)

                        retailrow = self._validate_row(starthour, endhour, group['branch_id'], branch_code, dis[:4])
                        output.write(retailrow)
                        output.write("\n")
                        retailline = self._validate_line(starthour, endhour, group['branch_id'], branch_code, dis[:4])
                        _logger.info(retailline)
                        output.write(retailline)
                        output.write("\n")
                        retaildivision = self._validate_division(starthour, endhour, group['branch_id'], branch_code, dis[:4])
                        _logger.info(retaildivision)
                        output.write(retaildivision)
                        output.write("\n")
                        retailgroup = self._validate_group(starthour, endhour, group['branch_id'], branch_code, dis[:4])
                        _logger.info(retailgroup)
                        output.write(retailgroup)
                        output.write("\n")
                        retaildept = self._validate_dept(starthour, endhour, group['branch_id'], branch_code, dis[:4])
                        _logger.info(retaildept)
                        output.write(retaildept)
                        output.write("\n")

                        store = str(branch_code)
                        master_code_file = base64.encodebytes(output.getvalue().encode('utf-8'))
                        # trans_count = self.env['pos.trans.code'].search_count([('date', '=', datetime.now()), ('flag_number','=', store)])
                        datenow = datetime.now().date()
                        sql_trans_pos_count="""select count(*) from pos_trans_code where DATE(date)= '{}' and flag_number='{}'""".format(datenow, store)
                        self.env.cr.execute(sql_trans_pos_count)
                        trans_count = self.env.cr.dictfetchall()
                        for total_count in trans_count:
                            lastnumb = total_count['count']
                            _logger.info("LASTNUMBER")
                            _logger.info(trans_count)
                            _logger.info(lastnumb)

                        numb = 0
                        if lastnumb == 12 or lastnumb == 0: 
                            numb = 1
                        else:
                            numb = lastnumb+1

                        filename = self.file_name(numb)
                        
                        _logger.info(store)
                        filename = filename+store[0]+'.'+store[1:]
                        _logger.info(filename)
                        # output.close()
                        vals = {
                            'master_code_file': master_code_file,
                            'master_code_filename': filename,
                            'flag_number': store
                        }
                        _logger.info(vals)
                        self.create(vals)
                        # master_code_file.close()
                        self.env.cr.commit()

    date = fields.Datetime(
        string='Datetime',
        default=fields.Datetime.now,
    )
    master_code_filename = fields.Char(
        string='File Name',
        readonly=True, default="pos_trans_code.txt"
    )
    master_code_file = fields.Binary(
        string='File',
        readonly=True,
    )
    flag_number = fields.Char(
        string='flag number',
    )
    
    

    