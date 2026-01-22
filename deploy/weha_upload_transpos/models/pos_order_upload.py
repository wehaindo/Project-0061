from ast import Store
from importlib.abc import FileLoader
from unittest import skipUnless
from odoo import _, api, fields, models
from datetime import datetime, timedelta, date
from dateutil.relativedelta import *
from io import StringIO
import io
import base64

import logging

_logger = logging.getLogger(__name__)

class pos_order_file(models.Model):
    _name = "pos.order.file"
    _description = "Pos Order File"
    _rec_name="filename"


    def item_record(self, line, row):
        # HEADER
        branch_code = line.branch_id.code
        if line.is_refunded == False:
            sni_comment = str("0043").zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 
        else:
            sni_comment = str("0044").zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 

        store_number = str(branch_code).ljust(4, '0')
        flags = "00".zfill(2) # default '0'
        pos_regis_num = str(line.session_id.config_id.code).zfill(3).ljust(6," ")
        # pos_trans_num = str(int(''.join(filter(str.isdigit, line.name)))).zfill(7)
        if line.pos_reference:
            receipt_no = str(line.pos_reference).replace("Order","")
            pos_trans_num = str(int(receipt_no)).zfill(8)
        else:
            pos_trans_num = "0".zfill(8)
        sni_format = "A".zfill(1) # A-Item Record, B-Total Record, C-Payment Record, D-Cash Record, E-Tender Count Record

        header = f'{sni_comment}{store_number}{flags}{pos_regis_num}{pos_trans_num}{sni_format}'

        # TYPE A
        filler1 = "0".zfill(1) # default '0'
        if line.is_refunded == False:
            sni_sales_type = "0001".zfill(4) # 0001 - SALES , 0301 - RETURN
        else:
            sni_sales_type = "0301".zfill(4) # 0001 - SALES , 0301 - RETURN

        sku = str(row.product_id.default_code).zfill(13)
        qty = f"{row.qty:0.2f}".zfill(9)
        filler2 = "0".zfill(1)                                  # default '0'
        regular_sell = f"{row.price_subtotal_incl:0.2f}".zfill(22)
        filler3 = "0".zfill(1)                                  # default '0'
        actual_sell = f"{row.price_unit:0.2f}".zfill(22)
        filler4 = "0".zfill(1)                                  # default '0'
        staff_id = str(line.user_id.id).zfill(10)
        filler5 = "0".zfill(1)                                  # default '0'
        lay_by_flag = "0".zfill(2)                              # default '0'
        filler6 = "0".zfill(1)                                  # default '0'
        disc_type = "00".zfill(2)                               # default '0'
        filler7 = "0".ljust(4, ' ')                             # default '0'
        acs_disc_amount = f"{float('0'):0.2f}".zfill(8)         # default '0'
        dept_num = str(row.product_id.dept_id.code).zfill(4)
        gift_voucher_from = "0".zfill(6)                        # default '0'
        gift_voucher_to = "0".zfill(6)                          # default '0'
        denom_val = "0".zfill(6)                                # default '0'
        for tx in row.tax_ids_after_fiscal_position:
            if tx.tax_type == "ppn":
                ppn_am = row.price_subtotal_incl - row.price_subtotal
                ppn_amount = f"{ppn_am:0.2f}".zfill(17)
                if tx.code:
                    ppn_code = str(tx.code).zfill(4)
                    tax_code = str(tx.code).zfill(5)
                else:
                    ppn_code = "0000".zfill(4)
                    tax_code = "00".zfill(5)
                sales_tax_amount = f"{float(0):0.2f}".zfill(15)
            else:
                ppn_am = row.price_subtotal_incl - row.price_subtotal
                ppn_amount = f"{0:0.2f}".zfill(17)
                ppn_code = "0000".zfill(4)
                tax_code = "00".zfill(5)
                sales_tax_amount = f"{float(ppn_am):0.2f}".zfill(15)
            break
        sales_person_id = "0".zfill(5)                          # default '0'
        lay_by_num = "0".zfill(10)                              # default '0'
        filler18 = "00".zfill(2)                                # default '0'
        sales_type = "02".zfill(2)                              # 01-Barcode, 02-Short SKU
        filler20 = "0".zfill(1)                                 # default '0'
        session = line.session_id.name[4:] or "0"
        cashier_id = str(session).zfill(7)
        member_price_disc = f"{float('0'):0.2f}".zfill(15)
        if row.price_source == "mix_and_match":
            mix_and_max_disc = f'{row.price_subtotal_incl}'.zfill(15)
        else: 
            mix_and_max_disc = f"{float('0'):0.2f}".zfill(15)
        total_received_disc = f"{float('0'):0.2f}".zfill(15)
        pos_disc = f"{float('0'):0.2f}".zfill(15) # Manual Disc
        staff_disc = f"{float('0'):0.2f}".zfill(15)             # default '0'
        perishable_disc = f"{float('0'):0.2f}".zfill(15)        # default '0'
        article_disc = f"{float('0'):0.2f}".zfill(15)           # default '0'
        sttd_disc = f"{float('0'):0.2f}".zfill(15)              # default '0'
        promotion_disc = f"{float('0'):0.2f}".zfill(15) 
        mfr_disc = f"{float('0'):0.2f}".zfill(15)               # default '0'
        price_change_promo_no = "".ljust(10, " ") 
        price_change_member_no = "".ljust(10, " ")
        mix_and_max_no = "".ljust(10, " ") 
        group_price_change = "".ljust(10, " ") 
        privilege_member = "N".zfill(1)                         # Default 'N' if press privilege in pos return value 'Y'
        over_write_flag = "N".zfill(1)                          # default 'N'
        cdo_no = "".ljust(12, " ")                              # default ''
        mommy_card_disc = f"{float('0'):0.2f}".zfill(15)        # default '0'
        member_card_disc = f"{float('0'):0.2f}".zfill(15)
        # tax_am = 0.00
        # for tax in row.tax_ids_after_fiscal_position:
        #     tax_am += tax.amount
        # sales_tax_amount = f"{float(tax_am):0.2f}".zfill(15)

        item_record = f"{filler1}{sni_sales_type}{sku}{qty}{filler2}{regular_sell}{filler3}{actual_sell}{filler4}{staff_id}{filler5}{lay_by_flag}{filler6}{disc_type}{filler7}{acs_disc_amount}{dept_num}{gift_voucher_from}{gift_voucher_to}{denom_val}{ppn_amount}{ppn_code}{sales_person_id}{lay_by_num}{filler18}{sales_type}{filler20}{cashier_id}{member_price_disc}{mix_and_max_disc}{total_received_disc}{pos_disc}{staff_disc}{perishable_disc}{article_disc}{sttd_disc}{promotion_disc}{mfr_disc}{price_change_promo_no}{price_change_member_no}{mix_and_max_no}{group_price_change}{privilege_member}{over_write_flag}{cdo_no}{mommy_card_disc}{member_card_disc}{tax_code}{sales_tax_amount}"
        master_code = f"{header}{item_record}\n"
        return master_code
            
    def total_record(self, line, row):
        # Summary Sales berdasarkan tipe pajak item
        # HEADER
        branch_code = line.branch_id.code
        if line.is_refunded == False:
            sni_comment = "0043".zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 
        else:
            sni_comment = "0044".zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 

        store_number = str(branch_code).ljust(4, '0')
        flags = "0".zfill(2)  # default '0'
        pos_regis_num = str(line.session_id.config_id.code).zfill(3).ljust(6," ")
        # pos_trans_num = str(int(''.join(filter(str.isdigit, line.name)))).zfill(7)
        if line.pos_reference:
            receipt_no = str(line.pos_reference).replace("Order","")
            pos_trans_num = str(int(receipt_no)).zfill(8)
        else:
            pos_trans_num = "0".zfill(8)
        sni_format = "B".zfill(1) # A-Item Record, B-Total Record, C-Payment Record, D-Cash Record, E-Tender Count Record

        header = f"{sni_comment}{store_number}{flags}{pos_regis_num}{pos_trans_num}{sni_format}"
        
        # TYPE B
        filler1 = "0"   # default '0'
        if line.is_refunded == False:
            sni_sales_type = "0011".zfill(4) # 0011 - SALES, 0311 - RETURN
        else:
            sni_sales_type = "0311".zfill(4) # 0011 - SALES, 0311 - RETURN

        if int(line.amount_tax) != 0:
            with_tax = line.amount_total
            total_amount_with_tax = f"{line.amount_total:0.2f}".zfill(23)
            with_nontax = float(0)
            total_amount_with_nontax = f"{float(0):0.2f}".zfill(23)
        else:
            with_tax = float(0)
            total_amount_with_tax = f"{float(0):0.2f}".zfill(23)
            with_nontax = line.amount_total
            total_amount_with_nontax = f"{line.amount_total:0.2f}".zfill(23)

        tax_amount = f"{line.amount_tax:0.2f}".zfill(15)            # Total pajak
        filler05 = "0".zfill(6)                                     # default '0'
        total_vat = with_tax + with_nontax + line.amount_tax
        total_amount_amt = f"{total_vat:0.2f}".zfill(23)            # Total Amount (with VAT) B002 + B003 + B004
        filler06 = "0".zfill(9)                                     # default '0'
        create_date = line.create_date
        sales_date = str(create_date.strftime("%Y%m%d")).zfill(8)
        sales_time = str(create_date.strftime("%H%M")).zfill(4)
        positive_total = "0".zfill(8)
        negative_total = "0".zfill(8)
        filler12 = "0".zfill(12)                                    # default '0'
        rounding_amount = f"{float(0):0.2f}".zfill(8)
        change_type = "00".zfill(2)
        change_amount = f"{float(0):0.2f}".zfill(18)
        gui_number = "0".zfill(10)                                  # default '0'
        member_card = "".ljust(20, " ")
        kadsim_card = "".ljust(20, " ")                             # default ''
        mommy_card = "".ljust(20, " ")                              # default ''
        refund_number = "".ljust(8, " ")                            # default ''
        refund_store_code = "".ljust(4, " ")                        # default ''
        refund_trans_date = "".ljust(8, " ")                        # default ''
        pre_booking_no = "".ljust(20, " ")                          # default ''
        refund_reason = "".ljust(4, " ")                            # default ''
        refund_description = "".ljust(100, " ")                     # default ''
        sales_tax_amount = f"{float(0):0.2f}".zfill(15)
        service_charge_amount = f"{float(0):0.2f}".zfill(15)        # default '0'

        total_record = f"{filler1}{sni_sales_type}{total_amount_with_tax}{total_amount_with_nontax}{tax_amount}{filler05}{total_amount_amt}{filler06}{sales_date}{sales_time}{positive_total}{negative_total}{filler12}{rounding_amount}{change_type}{change_amount}{gui_number}{member_card}{kadsim_card}{mommy_card}{refund_number}{refund_store_code}{refund_trans_date}{pre_booking_no}{refund_reason}{refund_description}{sales_tax_amount}{service_charge_amount}"
        master_code = f"{header}{total_record}\n"

        return master_code

    def payment_record(self, line, row, payment):
        # Summary sales berdasarkan Payment Type berdasakan kode kartu
        # HEADER
        branch_code = line.branch_id.code
        if line.is_refunded == False:
            sni_comment = "0043".zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 
        else:
            sni_comment = "0044".zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 

        store_number = str(branch_code).ljust(4, '0')
        flags = "0".zfill(2) # default '0'
        pos_regis_num = str(line.session_id.config_id.code).zfill(3).ljust(6," ")
        # pos_trans_num = str(int(''.join(filter(str.isdigit, line.name)))).zfill(7)
        if line.pos_reference:
            receipt_no = str(line.pos_reference).replace("Order","")
            pos_trans_num = str(int(receipt_no)).zfill(8)
        else:
            pos_trans_num = "0".zfill(8)
        sni_format = "C".zfill(1) # A-Item Record, B-Total Record, C-Payment Record, D-Cash Record, E-Tender Count Record

        header = f"{sni_comment}{store_number}{flags}{pos_regis_num}{pos_trans_num}{sni_format}"

        # TYPE C
        filler1 = "0" # default '0'
        if line.is_refunded == False:
            sni_sales_type = str("0012").zfill(4) # 0012 - SALES, 0312 - RETURN
        else:
            sni_sales_type = str("0312").zfill(4) # 0012 - SALES, 0312 - RETURN

        filler = "0".zfill(3)                                       # default '0'
        payment_amount = f"{line.amount_total:0.2f}".zfill(23)

        if payment.payment_method_id.code:
            payment_type = str(payment.payment_method_id.code).zfill(3)
        else:
            payment_type = "".zfill(3)

        if payment.payment_method_id.pos_pay_type_code:
            pos_pay_type_code = str(payment.payment_method_id.pos_pay_type_code).ljust(8, ' ')
        else:
            pos_pay_type_code = "00".ljust(8, ' ')
        # PAN
        if payment.pan:
            card_number = str(payment.pan).ljust(20, ' ')
        else:
            card_number = "000000******0000".ljust(20, ' ')
        # MID
        if payment.merchant_id:
            merchant_code = str(payment.merchant_id).ljust(22, ' ')
        else:
            merchant_code = "0".ljust(22, ' ')
        # approval code
        if payment.approval_code:
            approval_code = str(payment.approval_code).zfill(6)
        else:
            approval_code = "0".zfill(6)
        # TID
        if payment.terminal_id:
            terminal_id = str(payment.terminal_id).ljust(8, ' ')
        else:
            terminal_id = "".ljust(8, ' ')
        
        if payment.payment_method_id.credit_card_trace_no:
            trace_no = str(payment.payment_method_id.credit_card_trace_no).ljust(10, ' ')
        else:
            trace_no = "".ljust(10, ' ')

        actual_amt = f"{line.amount_total:0.2f}".zfill(23)
        debit_type = "".ljust(2, ' ')                               # default '0'
        trans_disc_amount = f"{float('0'):0.2f}".zfill(15)          # default '0'
        trans_disc_rate = f"{float('0'):0.2f}".zfill(6)             # default '0'
        approval_type = " "                                         # default '0'
        eco_point = "0"                                             # default '0'
        non_disc_amt = f"{float('0'):0.2f}".zfill(15)               # default '0'
        sales_tax_amt = f"{float('0'):0.2f}".zfill(15)              # default '0'
        foreign_currency_rate = f"{float('1'):0.2f}".zfill(6)       # default '0'
        filler3 = "0".zfill(2)                                      # default '0'
        other_bank = "N"

        payment_record = f"{filler1}{sni_sales_type}{payment_type}{filler}{payment_amount}{pos_pay_type_code}{card_number}{merchant_code}{actual_amt}{approval_code}{debit_type}{trans_disc_amount}{trans_disc_rate}{approval_type}{eco_point}{non_disc_amt}{sales_tax_amt}{terminal_id}{trace_no}{foreign_currency_rate}{filler3}{other_bank}"
        master_code = f"{header}{payment_record}\n"

        return master_code

    def cash_record(self, line, row, total_cash_count, total_cash):
        # Summary sales berdasarkan sales bertipe cash, dan inputan cashier berdasarkan perhitungan fisik cash drawer
        # HEADER
        branch_code = line.branch_id.code
        if line.is_refunded == False:
            sni_comment = "0043".zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 
        else:
            sni_comment = "0044".zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 
 
        store_number = str(branch_code).ljust(4, '0')
        flags = "0".zfill(2)  # default '0'
        pos_regis_num = str(line.session_id.config_id.code).zfill(3).ljust(6," ")
        # pos_trans_num = str(int(''.join(filter(str.isdigit, line.name)))).zfill(7)
        if line.pos_reference:
            receipt_no = str(line.pos_reference).replace("Order","")
            pos_trans_num = str(int(receipt_no)).zfill(8)
        else:
            pos_trans_num = "0".zfill(8)
        sni_format = "D".zfill(1) # A-Item Record, B-Total Record, C-Payment Record, D-Cash Record, E-Tender Count Record

        header = f'{sni_comment}{store_number}{flags}{pos_regis_num}{pos_trans_num}{sni_format}'

        # TYPE D
        filler1 = "0"                                           # default '0'
        cashier_id = str(line.session_id.name)[4:].zfill(9)
        loan_amount = f"{float('0'):0.2f}".zfill(23)
        middle_collec_amount = f"{float('0'):0.2f}".zfill(23)
        cash_sales = f"{total_cash:0.2f}".zfill(23)             # default '0'
        filler2 = "0".zfill(10)                                 # default '0'
        cash_count = f"{float(total_cash_count):0.2f}".zfill(23)             # default '0'

        cash_record = f"{filler1}{cashier_id}{loan_amount}{middle_collec_amount}{cash_sales}{filler2}{cash_count}"
        master_record = f'{header}{cash_record}\n'

        return master_record
    
    def tender_count_record(self, line, row, trans_type_e):
        # Summary sales berdasarkan payment type
        # HEADER
        branch_code = line.branch_id.code
        if line.is_refunded == False:
            sni_comment = "0043".zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 
        else:
            sni_comment = "0044".zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 
 
        store_number = str(branch_code).ljust(4, '0')
        flags = "0".zfill(2)
        pos_regis_num = str(trans_type_e['pos_id']).zfill(3).ljust(6," ")
        # pos_trans_num = str(int(''.join(filter(str.isdigit, line.name)))).zfill(7)
        if line.pos_reference:
            # receipt_no = str(line.pos_reference).replace("Order","")
            pos_trans_num = str(int(''.join(filter(str.isdigit, trans_type_e['session_id'])))).zfill(8)
        else:
            pos_trans_num = "0".zfill(8," ")
        sni_format = "E".zfill(1) # A-Item Record, B-Total Record, C-Payment Record, D-Cash Record, E-Tender Count Record

        header = f'{sni_comment}{store_number}{flags}{pos_regis_num}{pos_trans_num}{sni_format}'

        # TYPE E
        filler1 = "0"                                   # default '0'
        if line.is_refunded == False:
            sni_sales_type = str("0012").zfill(4)   # 0012 - SALES, 0312 - RETURN
        else:
            sni_sales_type = str("0312").zfill(4)   # 0012 - SALES, 0312 - RETURN

        pos_id = str(trans_type_e['pos_id']).zfill(3)
        if trans_type_e['code']:
            payment_type = str(trans_type_e['code']).ljust(3," ")
        else:
            payment_type = "".ljust(3," ")
        if trans_type_e['payment_sales']:
            payment_sales = f"{float(trans_type_e['payment_sales']):0.2f}".zfill(23)
        else:
            payment_sales = f"{float('0'):0.2f}".zfill(23)

        if trans_type_e['payment_count']:
            payment_count = f"{float(trans_type_e['payment_count']):0.2f}".zfill(23)
        else:
            payment_count = f"{float('0'):0.2f}".zfill(23)

        tender_count_record = f'{filler1}{sni_sales_type}{pos_id}{payment_type}{payment_sales}{payment_count}'
        master_record = f'{header}{tender_count_record}\n'

        return master_record

    def summary_sales_all(self, line, row, max_row, total_sales_refund, sales_rcpt_c, return_rcpt_c):
        # Summary sales keseluruhan data
        # HEADER
        branch_code = line.branch_id.code
        if line.is_refunded == False:
            sni_comment = "0043".zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 
        else:
            sni_comment = "0044".zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 
 
        store_number = str(branch_code).ljust(4, '0')
        flags = "0".zfill(2)      # default '0'
        pos_regis_num = str(line.session_id.config_id.code).zfill(3).ljust(6," ")
        # pos_trans_num = str(int(''.join(filter(str.isdigit, line.name)))).zfill(7)
        if line.pos_reference:
            receipt_no = str(line.pos_reference).replace("Order","")
            pos_trans_num = str(int(receipt_no)).zfill(8)
        else:
            pos_trans_num = "0".zfill(8)
        sni_format = "T".zfill(1) # A-Item Record, B-Total Record, C-Payment Record, D-Cash Record, E-Tender Count Record

        header = f'{sni_comment}{store_number}{flags}{pos_regis_num}{pos_trans_num}{sni_format}'

        # TYPE T
        filler1 = "0"                                           # default '0'
        line_count = str(max_row).zfill(8)
        total_sales_amount = f"{float(total_sales_refund):0.2f}".zfill(23)
        total_redeem_coupon = "0".zfill(8)
        value_redeem_coupon = f"{float('0'):0.2f}".zfill(23)
        sales_rcpt_count = str(sales_rcpt_c).zfill(8)
        return_rcpt_count = str(return_rcpt_c).zfill(8)
        rounding_amt = "0".ljust(10, ' ')

        summary_sales_all = f"{filler1}{line_count}{total_sales_amount}{total_redeem_coupon}{value_redeem_coupon}{sales_rcpt_count}{return_rcpt_count}{rounding_amt}"
        master_record = f"{header}{summary_sales_all}\n"

        return master_record

    
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
        filename = "S{}{}{}{}".format(Y, M, D, RR.upper())

        return filename

    def get_pos_order_upload(self):
        date_time = datetime.now() # + timedelta(days=-1)
        str_start_date = str(date_time.year)+ "-" + str(date_time.month).zfill(2) + "-" + str(date_time.day).zfill(2) + " " + "00:00:00"
        start_date_time = datetime.strptime(str_start_date, "%Y-%m-%d %H:%M:%S") - relativedelta(hours=7)
        # - relativedelta(hours=7)

        str_end_date = str(date_time.year) + "-" + str(date_time.month).zfill(2) + "-" + str(date_time.day).zfill(2) + " " + "23:59:59"
        end_date_time = datetime.strptime(str_end_date, "%Y-%m-%d %H:%M:%S") - relativedelta(hours=7)
        # - relativedelta(hours=7)

        sqlgroup="""SELECT a.branch_id, b.code as branch_code FROM pos_order a
            LEFT JOIN res_branch b ON a.branch_id = b.id
            WHERE a.create_date BETWEEN '{}' AND '{}'
            GROUP BY a.branch_id, b.code""".format(start_date_time, end_date_time) # .format(start_date_time, end_date_time) WHERE create_date BETWEEN '{}' AND '{}'
        self.env.cr.execute(sqlgroup)
        groups = self.env.cr.dictfetchall()
        if len(groups) > 0:
            for group in groups:
                output = StringIO()
                args = [('branch_id','=', group['branch_id']), ('create_date','>=', start_date_time), ('create_date','<=', end_date_time)] # , ('create_date','>=', start_date_time), ('create_date','<=', end_date_time)
                orders = self.env['pos.order'].search(args, order='id asc')
                max_row = 0
                total_refund = 0.0
                total_sales = 0.0
                sales_rcpt_c = 0
                return_rcpt_c = 0
                cash_count = 0
                total_cash = 0.0
                for line in orders:
                    for row in line.lines:
                        item_record = self.item_record(line, row) # TYPE A
                        output.write(item_record)
                        _logger.info(item_record)
                        max_row += 1
                        if row.price_subtotal < 0:
                            total_refund += row.price_subtotal
                        else:
                            total_sales += row.price_subtotal
                    
                    total_record = self.total_record(line, row) # TYPE B
                    output.write(total_record)
                    _logger.info(total_record)
                    max_row += 1
                    for payment in line.payment_ids:
                        payment_record = self.payment_record(line, row, payment) # TYPE C
                        output.write(payment_record)
                        _logger.info(payment_record)
                        max_row += 1
                    if line.is_refunded == False:
                        sales_rcpt_c += 1
                    else:
                        return_rcpt_c += 1

                    for rec in line.payment_ids:
                        if rec.payment_method_id.code == "CSH":
                            total_cash += rec.amount
                            cash_count += 1

                cash_record = self.cash_record(line, row, cash_count, total_cash) # TYPE D
                output.write(cash_record)
                _logger.info(cash_record)
                max_row += 1
                sqlgroup_type_e = """SELECT e.code as pos_id, d.name as session_id, c.code, sum(b.amount) as payment_sales, sum(f.amount) as payment_count
                        FROM pos_order a
                        LEFT JOIN pos_payment b ON a.id = b.pos_order_id
                        LEFT JOIN pos_payment_method c ON b.payment_method_id = c.id
                        LEFT JOIN pos_session d ON a.session_id = d.id
                        LEFT JOIN pos_config e ON d.config_id = e.id
                        LEFT JOIN account_bank_statement_line f ON d.id = f.pos_session_id
                        WHERE a.create_date BETWEEN '{}' AND '{}'
                        GROUP BY e.code, d.name, c.code ORDER BY d.name""".format(start_date_time, end_date_time)
                self.env.cr.execute(sqlgroup_type_e)
                groups_type_e = self.env.cr.dictfetchall()
                for trans_type_e in groups_type_e:
                    tender_count_record = self.tender_count_record(line, row, trans_type_e) # TYPE E
                    output.write(tender_count_record)
                    _logger.info(tender_count_record)
                    max_row += 1
                total_sales_refund = total_sales + total_refund
                summary_sales_all = self.summary_sales_all(line, row, max_row, total_sales_refund, sales_rcpt_c, return_rcpt_c) # TYPE T
                output.write(summary_sales_all)
                _logger.info(summary_sales_all)

                store = str(group['branch_code'])
                master_code_file = base64.encodebytes(output.getvalue().encode('utf-8'))
                datenow = datetime.now().date()
                # trans_count = self.env['pos.order.file'].search_count([('date', '=', datenow), ('flag_number','=', store)])
                sql="""select count(*) from pos_order_file where DATE(date)= '{}' and flag_number='{}'""".format(datenow, store)
                self.env.cr.execute(sql)
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
                filename = f'{filename}{store[0]}.{store[1:]}'
                _logger.info(filename)
                # output.close()
                vals = {
                    'file': master_code_file,
                    'filename': filename,
                    'flag_number': store
                }
                _logger.info(vals)
                self.create(vals)

        self.env.cr.commit()

    date = fields.Datetime(
        string='Datetime',
        default=fields.Datetime.now,
    )
    filename = fields.Char(
        string='File Name',
        readonly=True, default="pos_trans_code.txt"
    )
    file = fields.Binary(
        string='File',
        readonly=True,
    )
    flag_number = fields.Char(
        string='flag number',
    )
    