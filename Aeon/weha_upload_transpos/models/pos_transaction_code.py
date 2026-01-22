from odoo import _, api, fields, models
from datetime import datetime, timedelta, date
from dateutil.relativedelta import *
from io import StringIO
import io
import base64
import time
import logging

_logger = logging.getLogger(__name__)

class GenerateTransPOS(models.Model):
    _name = "pos.trans.code"
    _description = "POS Transaction Code"
    _rec_name="master_code_filename"
    _order = 'date DESC'

    def generate_upload_file(self):
        # store_codes = ["7001",'7002']
        # file_paths = ["/profit/idn/upload/pos/7001/","/profit/idn/upload/pos/7002/"]
        # for i in range(2):            
        self.get_transpos()
          
    def action_save_to_directory(self, store_code):
        # /comm/idn/upload/pos/7001/
        # /profit/idn/upload/pos/7001/
        self.ensure_one()
        try:
            with open("/profit/idn/upload/pos/" + store_code + "/" + self.master_code_filename,  "wb") as fh:            
                fh.write(base64.decodebytes(self.master_code_file))
        except Exception as e:
            _logger.info(e)
            
    def file_name(self, lastnumb, assign_date_time=False):
        if not assign_date_time:             
            if time.tzname[0] == 'WIB':
                date_time = datetime.now()  # example : datetime(2023,6,25,14,10,00)
            else:
                date_time = datetime.now() + timedelta(hours=7)
        else:
            if time.tzname[0] == 'WIB':
                date_time = datetime.strptime(assign_date_time, "%Y-%m-%d %H:%M:%S")
            else:
                date_time = datetime.strptime(assign_date_time, "%Y-%m-%d %H:%M:%S")
        
        # date_time = datetime.now()
        # sequence number
        if lastnumb <= 28:
            number_RR = hex(lastnumb)
            if len(number_RR) > 3:
                RR = number_RR[2:]
            else:
                RR = "0"+number_RR[2:]
        else:
            RR = 'ZZ'

        Y = date_time.strftime("%Y")[3:]
        Month = date_time.strftime("%m")
        Month_Hex = hex(int(Month))
        M = Month_Hex[2:]
        D = date_time.strftime("%d")
        filename = "RH{}{}{}{}".format(Y, M, D, RR.upper())

        return filename
    
    def _validate_row(self, starthour, endhour, branch_id, branch_code, hour):
        sqlrow="""SELECT count(distinct(a.order_id)) as transaction_count
                FROM pos_order_line a
                LEFT JOIN pos_order b ON a.order_id = b.id
                LEFT JOIN product_product c ON a.product_id = c.id
                LEFT JOIN product_template d ON c.product_tmpl_id = d.id
                LEFT JOIN res_branch e ON b.branch_id = e.id
                WHERE b.date_order BETWEEN '{}' AND '{}' AND e.id={}
                GROUP BY a.order_id""".format(starthour, endhour, branch_id)
        self.env.cr.execute(sqlrow)
        lines = self.env.cr.dictfetchall()
        master_row = []
        line_code = str(branch_code).ljust(10, ' ')
        transaction_count = str(len(lines)).rjust(7, ' ')
        master = f'{branch_code}STR{line_code}{hour}{transaction_count}'
        master_row.append(master)


        # for line in lines:
        #     line_code = str(branch_code).ljust(10, ' ')
        #     transaction_count = str(line["transaction_count"]).rjust(7, ' ')
        #     master = f'{branch_code}STR{line_code}{hour}{transaction_count}'
        #     master_row.append(master)

        master_row_join = '\n'.join(master_row)
        return master_row_join

    #Line
    def _validate_line(self, starthour, endhour, branch_id, branch_code, hour):
        _logger.info('validate_line')
        sqlline="""SELECT 
                j.code, count(distinct(a.order_id)) as customer_count
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
                GROUP BY j.code""".format(starthour, endhour, branch_id)    
        _logger.info(sqlline)    
        self.env.cr.execute(sqlline)
        divisions = self.env.cr.dictfetchall()
        _logger.info('_validate_line')
        _logger.info(divisions)
        master_division = []
        for division in divisions:
            division_code = str(division["code"]).ljust(10, ' ')
            customer_count = str(division["customer_count"]).rjust(7, ' ')
            # master_line = "{}DPT{}       {}       {}\n".format(branch_code, line['code'], hour, line['customer_count'])
            master = f'{branch_code}DPT{division_code}{hour}{customer_count}'
            master_division.append(master)

        master_division_join = '\n'.join(master_division)
        return master_division_join
    
    #Division
    def _validate_division(self, starthour, endhour, branch_id, branch_code, hour):
        sqldivision="""SELECT 
                h.code, count(distinct(a.order_id)) as customer_count
                FROM pos_order_line a
                LEFT JOIN pos_order b ON a.order_id = b.id
                LEFT JOIN product_product c ON a.product_id = c.id
                LEFT JOIN product_template d ON c.product_tmpl_id = d.id
                LEFT JOIN res_branch e ON b.branch_id = e.id
                LEFT JOIN product_category f ON d.categ_id = f.id
                LEFT JOIN res_department g ON f.dept_id = g.id
                LEFT JOIN res_division h ON g.division_id = h.id
                WHERE b.date_order BETWEEN '{}' AND '{}' AND e.id={}
                GROUP BY h.code""".format(starthour, endhour, branch_id)
        self.env.cr.execute(sqldivision)
        groups = self.env.cr.dictfetchall()
        _logger.info('_validate_division')
        _logger.info(groups)
        master_group = []
        for group in groups:
            group_code = str(group["code"]).ljust(10, ' ')
            customer_count = str(group["customer_count"]).rjust(7, ' ')
            # master_line = "{}DPT{}       {}       {}\n".format(branch_code, line['code'], hour, line['customer_count'])
            master = f'{branch_code}SEC{group_code}{hour}{customer_count}'
            master_group.append(master)

        master_group_join = '\n'.join(master_group)
        return master_group_join

    #Group
    def _validate_group(self, starthour, endhour, branch_id, branch_code, hour):
        sqlgroup="""SELECT 
                g.code,  count(distinct(a.order_id)) as customer_count
                FROM pos_order_line a
                LEFT JOIN pos_order b ON a.order_id = b.id
                LEFT JOIN product_product c ON a.product_id = c.id
                LEFT JOIN product_template d ON c.product_tmpl_id = d.id
                LEFT JOIN res_branch e ON b.branch_id = e.id
                LEFT JOIN product_category f ON d.categ_id = f.id
                LEFT JOIN res_department g ON f.dept_id = g.id
                WHERE b.date_order BETWEEN '{}' AND '{}' AND e.id={}
                GROUP BY g.code""".format(starthour, endhour, branch_id)
        self.env.cr.execute(sqlgroup)
        depts = self.env.cr.dictfetchall()
        master_dept = []
        for dept in depts:
            dept_code = str(dept["code"]).ljust(10, ' ')
            customer_count = str(dept["customer_count"]).rjust(7, ' ')
            # master_line = "{}DPT{}       {}       {}\n".format(branch_code, line['code'], hour, line['customer_count'])
            master = f'{branch_code}TYP{dept_code}{hour}{customer_count}'
            master_dept.append(master)

        master_dept_join = '\n'.join(master_dept)
        return master_dept_join

    #Department
    def _validate_dept(self, starthour, endhour, branch_id, branch_code, hour):
        sqlline="""SELECT 
                f.code, count(distinct(a.order_id)) as customer_count
                FROM pos_order_line a
                LEFT JOIN pos_order b ON a.order_id = b.id
                LEFT JOIN product_product c ON a.product_id = c.id
                LEFT JOIN product_template d ON c.product_tmpl_id = d.id
                LEFT JOIN res_branch e ON b.branch_id = e.id                
                LEFT JOIN product_category f ON d.categ_id = f.id
                WHERE a.create_date BETWEEN '{}' AND '{}' AND e.id={}
                GROUP BY f.code""".format(starthour, endhour, branch_id)
        self.env.cr.execute(sqlline)
        categories = self.env.cr.dictfetchall()
        master_category = []
        for category in categories:
            categ_code = str(category["code"]).ljust(10, ' ')
            customer_count = str(category["customer_count"]).rjust(7, ' ')
            # master_line = "{}DPT{}       {}       {}\n".format(branch_code, line['code'], hour, line['customer_count'])
            master = f'{branch_code}ART{categ_code}{hour}{customer_count}'
            master_category.append(master)

        master_category_join = '\n'.join(master_category)
        return master_category_join

    @api.model
    def get_transpos(self, assign_date_time=False):
        _logger.info('get_transpos')

        def convert_price_subtotal(price_subtotal):
            if price_subtotal >= 0.0:
                arr = str(price_subtotal).split(".")
                left_val = arr[0]
                right_val = arr[1][:2]
                return left_val.zfill(20) + right_val.ljust(2,"0")
            else:
                arr = str(price_subtotal).split(".")
                left_val = arr[0]
                right_val = arr[1][:2]
                # return "-" + left_val.zfill(21) + right_val.ljust(2,"0")
                return left_val.zfill(20) + right_val.ljust(2,"0")
                                            
        def convert_price_subtotal_incl(price_subtotal_incl):
            if price_subtotal_incl >= 0.0:
                arr = str(price_subtotal_incl).split(".")
                left_val = arr[0]
                right_val = arr[1][:2]
                return left_val.zfill(20) + right_val.ljust(2,"0")
            else:
                arr = str(price_subtotal_incl).split(".")
                left_val = arr[0]
                right_val = arr[1][:2]
                return left_val.zfill(20) + right_val.ljust(2,"0")
            
        try:
            check_hour = {                
                "1": ["08:00:00","08:30:00"], 
                "2": ["08:30:00","09:00:00"], 
                "3": ["09:00:00","09:30:00"],                 
                "4": ["09:30:00","10:00:00"], 
                "5": ["10:00:00","10:30:00"], 
                "6": ["10:30:00","11:00:00"], 
                "7": ["11:00:00","11:30:00"],
                "8": ["11:30:00","12:00:00"], 
                "9": ["12:00:00","12:30:00"], 
                "10": ["12:30:00","13:00:00"], 
                "11": ["13:00:00","13:30:00"], 
                "12": ["13:30:00","14:00:00"],
                "13": ["14:00:00","14:30:00"], 
                "14": ["14:30:00","15:00:00"], 
                "15": ["15:00:00","15:30:00"], 
                "16": ["15:30:00","16:00:00"], 
                "17": ["16:00:00","16:30:00"], 
                "18": ["16:30:00","17:00:00"], 
                "19": ["17:00:00","17:30:00"], 
                "20": ["17:30:00","18:00:00"], 
                "21": ["18:00:00","18:30:00"], 
                "22": ["18:30:00","19:00:00"], 
                "23": ["19:00:00","19:30:00"], 
                "24": ["19:30:00","20:00:00"], 
                "25": ["20:00:00","20:30:00"], 
                "26": ["20:30:00","21:00:00"], 
                "27": ["21:00:00","21:30:00"], 
                "28": ["21:30:00","22:00:00"], 
                "29": ["22:00:00","22:30:00"], 
            }

            if not assign_date_time:             
                if time.tzname[0] == 'WIB':
                    date_time = datetime.now()  + timedelta(minutes=2)# example : datetime(2023,6,25,14,10,00)           
                    check_date_time = datetime.now()   + timedelta(minutes=2)       
                else:
                    date_time = datetime.now() + timedelta(hours=7,minutes=2)
                    check_date_time = datetime.now() + timedelta(hours=7, minutes=2)         

            else:
                if time.tzname[0] == 'WIB':
                    date_time = datetime.strptime(assign_date_time, "%Y-%m-%d %H:%M:%S") + timedelta(minutes=2)
                    check_date_time = datetime.strptime(assign_date_time, "%Y-%m-%d %H:%M:%S")  + timedelta(minutes=2)
                else:
                    date_time = datetime.strptime(assign_date_time, "%Y-%m-%d %H:%M:%S") + timedelta(minutes=2)
                    check_date_time = datetime.strptime(assign_date_time, "%Y-%m-%d %H:%M:%S") + timedelta(minutes=2)

            time_hour_no = -1
            _logger.info('date_time')
            _logger.info(date_time)
            if date_time > check_date_time.replace(hour=8,minute=0,second=0) and date_time < check_date_time.replace(hour=8,minute=30,second=0):
                time_hour_no = 0
            if date_time > check_date_time.replace(hour=8,minute=30,second=0) and date_time < check_date_time.replace(hour=9,minute=00,second=0):
                time_hour_no = 1
            if date_time > check_date_time.replace(hour=9,minute=0,second=0) and date_time < check_date_time.replace(hour=9,minute=30,second=0):
                time_hour_no = 2
            if date_time > check_date_time.replace(hour=9,minute=30,second=0) and date_time < check_date_time.replace(hour=10,minute=00,second=0):
                time_hour_no = 3
            if date_time > check_date_time.replace(hour=10,minute=0,second=0) and date_time < check_date_time.replace(hour=10,minute=30,second=0):
                time_hour_no = 4
            if date_time > check_date_time.replace(hour=10,minute=30,second=0) and date_time < check_date_time.replace(hour=11,minute=00,second=0):
                time_hour_no = 5
            if date_time > check_date_time.replace(hour=11,minute=0,second=0) and date_time < check_date_time.replace(hour=11,minute=30,second=0):
                time_hour_no = 6
            if date_time > check_date_time.replace(hour=11,minute=30,second=0) and date_time < check_date_time.replace(hour=12,minute=00,second=0):
                time_hour_no = 7
            if date_time > check_date_time.replace(hour=12,minute=0,second=0) and date_time < check_date_time.replace(hour=12,minute=30,second=0):
                time_hour_no = 8
            if date_time > check_date_time.replace(hour=12,minute=30,second=0) and date_time < check_date_time.replace(hour=13,minute=00,second=0):
                time_hour_no = 9
            if date_time > check_date_time.replace(hour=13,minute=0,second=0) and date_time < check_date_time.replace(hour=13,minute=30,second=0):
                time_hour_no = 10
            if date_time > check_date_time.replace(hour=13,minute=30,second=0) and date_time < check_date_time.replace(hour=14,minute=00,second=0):
                time_hour_no = 11
            if date_time > check_date_time.replace(hour=14,minute=0,second=0) and date_time < check_date_time.replace(hour=14,minute=30,second=0):
                time_hour_no = 12
            if date_time > check_date_time.replace(hour=14,minute=30,second=0) and date_time < check_date_time.replace(hour=15,minute=00,second=0):
                time_hour_no = 13
            if date_time > check_date_time.replace(hour=15,minute=0,second=0) and date_time < check_date_time.replace(hour=15,minute=30,second=0):
                time_hour_no = 14
            if date_time > check_date_time.replace(hour=15,minute=30,second=0) and date_time < check_date_time.replace(hour=16,minute=00,second=0):
                time_hour_no = 15
            if date_time > check_date_time.replace(hour=16,minute=0,second=0) and date_time < check_date_time.replace(hour=16,minute=30,second=0):
                time_hour_no = 16
            if date_time > check_date_time.replace(hour=16,minute=30,second=0) and date_time < check_date_time.replace(hour=17,minute=00,second=0):
                time_hour_no = 17
            if date_time > check_date_time.replace(hour=17,minute=0,second=0) and date_time < check_date_time.replace(hour=17,minute=30,second=0):
                time_hour_no = 18
            if date_time > check_date_time.replace(hour=17,minute=30,second=0) and date_time < check_date_time.replace(hour=18,minute=00,second=0):
                time_hour_no = 19
            if date_time > check_date_time.replace(hour=18,minute=0,second=0) and date_time < check_date_time.replace(hour=18,minute=30,second=0):
                time_hour_no = 20
            if date_time > check_date_time.replace(hour=18,minute=30,second=0) and date_time < check_date_time.replace(hour=19,minute=00,second=0):
                time_hour_no = 21
            if date_time > check_date_time.replace(hour=19,minute=0,second=0) and date_time < check_date_time.replace(hour=19,minute=30,second=0):
                time_hour_no = 22
            if date_time > check_date_time.replace(hour=19,minute=30,second=0) and date_time < check_date_time.replace(hour=20,minute=00,second=0):
                time_hour_no = 23
            if date_time > check_date_time.replace(hour=20,minute=0,second=0) and date_time < check_date_time.replace(hour=20,minute=30,second=0):
                time_hour_no = 24
            if date_time > check_date_time.replace(hour=20,minute=30,second=0) and date_time < check_date_time.replace(hour=21,minute=00,second=0):
                time_hour_no = 25
            if date_time > check_date_time.replace(hour=21,minute=0,second=0) and date_time < check_date_time.replace(hour=21,minute=30,second=0):
                time_hour_no = 26
            if date_time > check_date_time.replace(hour=21,minute=30,second=0) and date_time < check_date_time.replace(hour=22,minute=00,second=0):
                time_hour_no = 27
            if date_time > check_date_time.replace(hour=22,minute=0,second=0) and date_time < check_date_time.replace(hour=22,minute=30,second=0):
                time_hour_no = 28
            if date_time > check_date_time.replace(hour=22,minute=30,second=0) and date_time < check_date_time.replace(hour=23,minute=00,second=0):
                time_hour_no = 29
                                    
            _logger.info('time_hour_no')
            _logger.info(time_hour_no)                                              
            if check_hour.get(str(time_hour_no)):                                            
                dis = check_hour[str(time_hour_no)][1].replace(':','')
                str_start_date = str(date_time.year)+ "-" + str(date_time.month).zfill(2) + "-" + str(date_time.day).zfill(2) + " " + "00:00:00"
                starthour = datetime.strptime(str_start_date, "%Y-%m-%d %H:%M:%S") - relativedelta(hours=7)                
                str_end_date = str(date_time.year) + "-" + str(date_time.month).zfill(2) + "-" + str(date_time.day).zfill(2) + " " + check_hour[str(time_hour_no)][1]
                endhour = datetime.strptime(str_end_date, "%Y-%m-%d %H:%M:%S") - relativedelta(hours=7)
                _logger.info("DATE")
                _logger.info(str(starthour))
                _logger.info(str(endhour))                                
                branch_list = ['7001','7002','7003','7004']
                sqlgroup="SELECT id as branch_id, code as branch_code FROM res_branch WHERE code IN %(branch_list)s"                    
                _logger.info(sqlgroup)
                self.env.cr.execute(sqlgroup,{'branch_list': tuple(branch_list)})            
                groups = self.env.cr.dictfetchall()
                _logger.info(str(groups))                               
                for group in groups:
                    _logger.info("START STRING-IO")
                    output = StringIO()
                    branch_code = group['branch_code']
                    sql_count="""SELECT
                        a.branch_id, e.code as branch_code, count(d.default_code) as customer_count, d.default_code
                        FROM pos_order_line a
                        LEFT JOIN pos_order b ON a.order_id = b.id
                        LEFT JOIN product_product c ON a.product_id = c.id
                        LEFT JOIN product_template d ON c.product_tmpl_id = d.id
                        LEFT JOIN res_branch e ON b.branch_id = e.id
                        WHERE b.date_order BETWEEN '{}' AND '{}' AND a.branch_id={}
                        GROUP BY a.branch_id, e.code, d.default_code""".format(starthour, endhour, group['branch_id'])
                    self.env.cr.execute(sql_count)
                    orders = self.env.cr.dictfetchall()
                    _logger.info("orders")
                    _logger.info(orders)
                    for order in orders:
                        _logger.info("ORDER BY STORE")
                        #branch_code = order['branch_code'].zfill(4)
                        #_logger.info(str(branch_code))
                        sql="""SELECT
                            e.code, d.default_code, sum(a.qty) as qty, sum(a.price_subtotal) as price_subtotal,  sum(a.price_subtotal_incl) as price_subtotal_incl
                            FROM pos_order_line a
                            LEFT JOIN pos_order b ON a.order_id = b.id
                            LEFT JOIN product_product c ON a.product_id = c.id
                            LEFT JOIN product_template d ON c.product_tmpl_id = d.id
                            LEFT JOIN res_branch e ON b.branch_id = e.id
                            WHERE b.date_order BETWEEN '{}' AND '{}' AND d.default_code='{}' AND a.branch_id={}
                            GROUP BY e.code, d.default_code""".format(starthour, endhour, order['default_code'], order['branch_id'])
                        _logger.info(sql)
                        self.env.cr.execute(sql)
                        lines = self.env.cr.dictfetchall()
                        for line in lines:
                            _logger.info(line)
                            qty = str(int(line['qty'])).zfill(10)
                            price_subtotal = convert_price_subtotal(line['price_subtotal'])
                            price_subtotal_incl = convert_price_subtotal_incl(line['price_subtotal_incl'])                           
                            master_code = "{}{}{}{}{}{}{}\n".format(line['code'].zfill(4), line['default_code'].ljust(13, ' '),
                                    dis[:4], qty, price_subtotal_incl, str(order['customer_count']).rjust(6, ' '), price_subtotal)
                            
                            output.write(master_code)
                            _logger.info(master_code)

                    if len(orders) > 0:
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
                    else:
                        output.write(' ')

                    store = str(branch_code)
                    master_code_file = base64.encodebytes(output.getvalue().encode('utf-8'))
                    
                    if not assign_date_time:
                        filename = self.file_name(time_hour_no)                        
                    else:
                        filename = self.file_name(time_hour_no, assign_date_time)                        
                    _logger.info("store")
                    _logger.info(store)
                    filename = filename+store[0]+'.'+store[1:]
                    _logger.info(filename)
                    # output.close()
                    vals = {
                        'master_code_file': master_code_file,
                        'master_code_filename': filename.upper(),
                        'flag_number': store
                    }
                    _logger.info(vals)
                    res = self.create(vals)                                                
                    self.env.cr.commit()
                    res.action_save_to_directory(store)
            else:
                _logger.info('Time not found')
        except Exception as e:
            _logger.error(e)

    date = fields.Datetime(
        string='Datetime',
        default=fields.Datetime.now,
    )
    master_code_filename = fields.Char(
        string='File Name',
        readonly=True
    )
    master_code_file = fields.Binary(
        string='File',
        readonly=True,
    )
    flag_number = fields.Char(
        string='flag number',
    )
    
    

    