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
    _order = 'date DESC'
    
    def generate_upload_file(self):
        vals = {
            'date': datetime.now()
        }
        res = self.env['pos.order.file'].create(vals)
        res.get_pos_order_upload()
        res.action_save_to_directory()

    def action_save_to_directory(self):
        # /comm/idn/upload/pos/7001/
        # /profit/idn/upload/pos/7001/
        with open("/profit/idn/upload/pos/7001/" + self.filename.upper(),  "wb") as fh:            
            fh.write(base64.decodebytes(self.file))

    def item_record(self, line, row, is_duplicate):
        # HEADER
        branch_code = line.branch_id.code
        if line.is_void == False and line.is_refund == False:
            sni_comment = str("0043").zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 
        else:
            if line.is_void == True:
                sni_comment = str("0045").zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 
            if line.is_refund == True:
                sni_comment = str("0044").zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 

        store_number = str(branch_code).ljust(4, '0')
        flags = "00".zfill(2) # default '0'
        pos_regis_num = str(line.session_id.config_id.code).zfill(3).ljust(6," ")
        # pos_trans_num = str(int(''.join(filter(str.isdigit, line.name)))).zfill(7)
        # if line.pos_reference:
        #     receipt_no = str(line.pos_reference).replace("Order","")
        #     pos_trans_num = str(int(receipt_no)).zfill(8)
        # else:
        #     pos_trans_num = "0".zfill(8)

        if line.pos_reference:
            if not is_duplicate:            
                receipt_no = str(line.pos_reference).replace("Order","")
                pos_trans_num = str(int(receipt_no)).zfill(8)
            else:
                receipt_no = str(line.pos_reference).replace("Order","")[-4:]
                order_ref = line.name.split('/')[1][-4:]
                pos_trans_num = order_ref + receipt_no                
        else:
            pos_trans_num = "0".zfill(8)


        sni_format = "A".zfill(1) # A-Item Record, B-Total Record, C-Payment Record, D-Cash Record, E-Tender Count Record

        header = f'{sni_comment}{store_number}{flags}{pos_regis_num}{pos_trans_num}{sni_format}'

        # TYPE A
        filler1 = "0".zfill(1) # default '0'
        if line.is_void == False and line.is_refund == False:
            sni_sales_type = "0001".zfill(4) # 0001 - SALES , 0301 - RETURN
        else:
            sni_sales_type = "0301".zfill(4) # 0001 - SALES , 0301 - RETURN

        sku = str(row.product_id.default_code).zfill(13)
        #_logger.info(sku)
        qty = f"{row.qty:0.2f}".zfill(9)
        filler2 = "0".zfill(1)                                  # default '0'
        regular_sell = f"{row.list_price:0.2f}".zfill(22)
        if line.is_void == False and line.is_refund == False:
            filler3 = "0".zfill(1)                                  # default '0'
        else:
            filler3 = "-".zfill(1)           
        # orderLine.get_unit_price() * (orderLine.get_discount()/100) * orderLine.get_quantity()
        # calc_actual_sell = (row.price_unit - (row.price_unit * (row.discount/100))) * row.qty 
        calc_actual_sell = row.price_subtotal_incl
        actual_sell = f"{calc_actual_sell:0.2f}".zfill(22)
        filler4 = "0".zfill(1)                                  # default '0'
        staff_id = str(line.user_id.id).zfill(10)
        filler5 = "0".zfill(1)                                  # default '0'
        lay_by_flag = "0".zfill(2)                              # default '0'
        filler6 = "0".zfill(1)                                  # default '0'
        disc_type = "00".zfill(2)                               # default '0'
        acs_disc_amount = f"{float('0'):0.2f}".zfill(8)         # default '0'
        filler7 = "0".ljust(4, ' ')                             # default '0'
        dept_num = str(row.product_id.dept_id.code).zfill(4)
        gift_voucher_from = "0000".ljust(6, " ")                # default '0'
        gift_voucher_to = "0".zfill(6)                          # default '0'
        denom_val = "0".zfill(8)                                # default '0'
        for tx in row.tax_ids_after_fiscal_position:
            if tx.tax_type == "ppn":
                ppn_am = row.price_subtotal_incl - row.price_subtotal
                ppn_amount = f"{ppn_am:0.2f}".zfill(15)
                if tx.code:
                    ppn_code = str(tx.code).zfill(4)
                    tax_code = str(tx.code).ljust(5, " ")
                else:
                    ppn_code = "".ljust(4, " ")
                    tax_code = "".ljust(5, " ")
                sales_tax_amount = f"{float(0):0.2f}".zfill(15)
                #sales_tax_ammount = f"{line.amount_tax:0.2f}".zfill(15)
            else:
                ppn_am = row.price_subtotal_incl - row.price_subtotal
                ppn_amount = f"{0:0.2f}".zfill(15)
                ppn_code = "".ljust(4, " ")
                tax_code = "".ljust(5, " ")
                sales_tax_amount = f"{float(ppn_am):0.2f}".zfill(15)
                #sales_tax_ammount = f"{line.amount_tax:0.2f}".zfill(15)
            break
        sales_person_id = "0".zfill(5)                          # default '0'
        lay_by_num = "0".zfill(10)                              # default '0'
        filler18 = "00".zfill(2)                                # default '0'
        sales_type = "02".zfill(2)                              # 01-Barcode, 02-Short SKU
        filler20 = "0".zfill(1)                                 # default '0'
        session = line.session_id.name[4:] or "0"
        cashier_id = str(row.order_id.user_id.login).zfill(7)
        
        if row.price_source == "pdcm":
            pdcm = row.list_price-row.price_unit
            member_price_disc = f"{pdcm:0.2f}".zfill(15)  
            if row.prc_no == '' or row.prc_no == 'False':
                pdcm = 0.0
                member_price_disc = f"{float('0'):0.2f}".zfill(15)
                price_change_member_no = "".ljust(10, " ")                
            else:
                price_change_member_no = str(row.prc_no).ljust(10, " ")
        else:
            pdcm = 0.0
            member_price_disc = f"{float('0'):0.2f}".zfill(15)
            price_change_member_no = "".ljust(10, " ")

        if row.price_source == "mix_and_match":
            mnm = row.list_price-row.price_unit
            mix_and_max_disc = f"{mnm:0.2f}".zfill(15)
            if row.prc_no == '' or row.prc_no == 'False':
                mnm = 0.0
                mix_and_max_disc = f"{float('0'):0.2f}".zfill(15)
                mix_and_max_no = "".ljust(10, " ")                
            else:
                mix_and_max_no = row.prc_no[4:].ljust(10, " ")
        else:
            mnm = 0.0
            mix_and_max_disc = f"{float('0'):0.2f}".zfill(15)
            mix_and_max_no = "".ljust(10, " ")

        if row.price_source == "override":
            override = row.list_price-row.price_unit
            pos_disc = f"{override:0.2f}".zfill(15)
        else:
            override = 0.0
            pos_disc = f"{float('0'):0.2f}".zfill(15) # Manual Disc

        staff_disc = f"{float('0'):0.2f}".zfill(15)             # default '0'
        perishable_disc = f"{float('0'):0.2f}".zfill(15)        # default '0'
        article_disc = f"{float('0'):0.2f}".zfill(15)           # default '0'
        sttd_disc = f"{float('0'):0.2f}".zfill(15)              # default '0'

        if row.price_source == "pdc":
            pdc = row.list_price-row.price_unit
            promotion_disc = f"{pdc:0.2f}".zfill(15)
            if row.prc_no == '' or row.prc_no == 'False':
                pdc = 0.0
                promotion_disc = f"{float('0'):0.2f}".zfill(15)
                price_change_promo_no = "".ljust(10, " ")                
            else:
                price_change_promo_no = row.prc_no and str(row.prc_no).ljust(10, " ") or "".ljust(10, " ")
        else:
            pdc = 0.0
            promotion_disc = f"{float('0'):0.2f}".zfill(15)
            price_change_promo_no = "".ljust(10, " ")
    
        mfr_disc = f"{float('0'):0.2f}".zfill(15)               # default '0'

        mommy_card_disc = f"{float('0'):0.2f}".zfill(15)    
        
        # member_card_disc = f"{float('0'):0.2f}".zfill(15)    # default '0    
        
        if row.discount > 0:
            member_day_discount = row.price_unit * (row.discount/100)
            member_card_disc = f"{member_day_discount:0.2f}".zfill(15)        
        else:
            member_day_discount = 0.0
            member_card_disc = f"{member_day_discount:0.2f}".zfill(15)    # default '0'


        total_received = pdcm + pdc + mnm + override
        total_received_disc = f"{float('0'):0.2f}".zfill(15)

        group_price_change = "".ljust(10, " ") 
        privilege_member = "N".zfill(1)                         # Default 'N' if press privilege in pos return value 'Y'
        over_write_flag = "N".zfill(1)                          # default 'N'
        cdo_no = "".ljust(12, " ")                              # default ''
        
        # tax_am = 0.00
        # for tax in row.tax_ids_after_fiscal_position:
        #     tax_am += tax.amount
        # sales_tax_amount = f"{float(tax_am):0.2f}".zfill(15)

        item_record = f'{filler1}{sni_sales_type}{sku}{qty}{filler2}{regular_sell}{filler3}{actual_sell}{filler4}{staff_id}{filler5}{lay_by_flag}{filler6}{disc_type}{filler7}{acs_disc_amount}{dept_num}{gift_voucher_from}{gift_voucher_to}{denom_val}{ppn_amount}{ppn_code}{sales_person_id}{lay_by_num}{filler18}{sales_type}{filler20}{cashier_id}{member_price_disc}{mix_and_max_disc}{total_received_disc}{pos_disc}{staff_disc}{perishable_disc}{article_disc}{sttd_disc}{promotion_disc}{mfr_disc}{price_change_promo_no}{price_change_member_no}{mix_and_max_no}{group_price_change}{privilege_member}{over_write_flag}{cdo_no}{mommy_card_disc}{member_card_disc}{tax_code}{sales_tax_amount}'
        master_code = f"{header}{item_record}\n"
        return master_code
            
    def total_record(self, line, row, is_duplicate):
        # Summary Sales berdasarkan tipe pajak item
        # HEADER
        branch_code = line.branch_id.code
        if line.is_void == False and line.is_refund == False:
            sni_comment = str("0043").zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 
        else:
            if line.is_void == True:
                sni_comment = str("0045").zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 
            if line.is_refund == True:
                sni_comment = str("0044").zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 

        store_number = str(branch_code).ljust(4, '0')
        flags = "0".zfill(2)  # default '0'
        pos_regis_num = str(line.session_id.config_id.code).zfill(3).ljust(6," ")
        # pos_trans_num = str(int(''.join(filter(str.isdigit, line.name)))).zfill(7)
        if line.pos_reference:
            if not is_duplicate:            
                receipt_no = str(line.pos_reference).replace("Order","")
                pos_trans_num = str(int(receipt_no)).zfill(8)
            else:
                receipt_no = str(line.pos_reference).replace("Order","")[-4:]
                order_ref = line.name.split('/')[1][-4:]
                pos_trans_num = order_ref + receipt_no                
                _logger.info('pos_trns_num')
                _logger.info(pos_trans_num)
        else:
            pos_trans_num = "0".zfill(8)
        sni_format = "B".zfill(1) # A-Item Record, B-Total Record, C-Payment Record, D-Cash Record, E-Tender Count Record

        header = f"{sni_comment}{store_number}{flags}{pos_regis_num}{pos_trans_num}{sni_format}"
        
        # TYPE B
        filler1 = "0"   # default '0'
        if line.is_void == False and line.is_refund == False:
            sni_sales_type = "0011".zfill(4) # 0011 - SALES, 0311 - RETURN
        else:
            sni_sales_type = "0311".zfill(4) # 0011 - SALES, 0311 - RETURN

        if int(line.amount_tax) != 0:
            with_tax = line.amount_paid
            without_tax = line.amount_total - line.amount_tax
            total_amount_with_tax = f"{with_tax:0.2f}".zfill(23)        
            total_amount_with_nontax = f"{without_tax:0.2f}".zfill(23)
            nontax_able= float(0)
            total_amount_with_nontax_able = f"{nontax_able:0.2f}".zfill(23)
        else:
            with_tax = float(0)
            total_amount_with_tax = f"{float(0):0.2f}".zfill(23)
            with_nontax = line.amount_paid
            total_amount_with_nontax = f"{line.amount_paid:0.2f}".zfill(23)
            total_amount_with_nontax_able = f"{line.amount_paid:0.2f}".zfill(23)

        tax_amount = f"{line.amount_tax:0.2f}".zfill(15)            # Total pajak
        filler05 = "0".zfill(6)                                     # default '0'
        #total_vat = with_tax + with_nontax + line.amount_tax
        total_vat = line.amount_tax
        total_amount_paid = f"{line.amount_paid:0.2f}".zfill(23) 
        total_amount_amt = f"{line.amount_total:0.2f}".zfill(23)            # Total Amount (with VAT) B002 + B003 + B004
        filler06 = "0".zfill(9)                                     # default '0'
        create_date = line.create_date
        sales_date = str(create_date.strftime("%Y%m%d")).zfill(8)
        sales_time = str(create_date.strftime("%H%M")).zfill(4)
        positive_total = "0".zfill(8)
        negative_total = "0".zfill(8)
        filler12 = "0".zfill(12)                                    # default '0'
        if line.is_void == False:
            if line.amount_total == line.amount_paid:
                rounding_amount = f"{float(0):0.2f}".zfill(8)
            else:
                diff_amount = line.amount_total - line.amount_paid
                rounding_amount = f"{-1 * diff_amount:0.2f}".zfill(8)            
        else:
            if line.amount_total == line.amount_paid:
                rounding_amount = f"{float(0):0.2f}".zfill(8)
            else:
                diff_amount = line.amount_total - line.amount_paid
                rounding_amount = f"{-1 * diff_amount:0.2f}".zfill(8)
                

        change_type = "00".zfill(2)
        change_amount = f"{float(0):0.2f}".zfill(18)
        gui_number = "0".zfill(10)                                  # default '0'
        member_card = "".ljust(20, " ")
        kadsim_card = "".ljust(20, " ")                             # default ''
        mommy_card = "".ljust(20, " ")                              # default ''
        
        if  line.is_void == False and line.is_refund == False:
            refund_number = "".ljust(8, " ")                            # default ''        
            refund_store_code = "".ljust(4, " ")                        # default ''
            refund_trans_date = "".ljust(8, " ")                        # default ''            
            pre_booking_no = "".ljust(20, " ")        # default ''
            refund_reason = "".ljust(4, " ")                            # default ''
            refund_description = "".ljust(100, " ")                     # default ''    
        else:
            if line.is_void:
                domain = [
                    ('pos_reference','=',line.void_parent_pos_reference)
                ]
                refund_parent_id = self.env['pos.order'].search(domain, limit=1)
                # _logger.info('void_parent_id')
                # _logger.info(refund_parent_id)
                refund_number = refund_parent_id.pos_reference.replace("Order","")[2:].ljust(8, " ")        # default ''
                refund_store_code = branch_code.ljust(4, " ")                                           # default ''
                refund_trans_date = refund_parent_id.date_order.strftime('%Y%m%d').ljust(8, " ")           # default ''            
                pre_booking_no = "".ljust(20, " ")                                                      # default ''
                refund_reason = "006".ljust(4, " ")                                                     # default ''
                refund_description = "".ljust(100, " ")                                                 # default ''
            else:
                # _logger.info(line.id)
                domain = [
                    ('pos_reference','=',line.refund_parent_pos_reference)
                ]
                # _logger.info(domain)
                refund_parent_id = self.env['pos.order'].search(domain, limit=1)
                # _logger.info('refund_parent_id')
                # _logger.info(refund_parent_id)
                refund_number = refund_parent_id.pos_reference.replace("Order","")[2:].ljust(8, " ")        # default ''
                refund_store_code = branch_code.ljust(4, " ")                                           # default ''
                refund_trans_date = refund_parent_id.date_order.strftime('%Y%m%d').ljust(8, " ")           # default ''            
                pre_booking_no = "".ljust(20, " ")                                                      # default ''
                refund_reason = "006".ljust(4, " ")                                                     # default ''
                refund_description = "".ljust(100, " ")   

        if line.is_void == False and line.is_refund == False:
            sales_tax_amount = f"{float(0):0.2f}".zfill(15)
            service_charge_amount = f"{float(0):0.2f}".zfill(15)        # default '0'
        else:
            sales_tax_amount = f"{-1 * float(0):0.2f}".zfill(15)
            service_charge_amount = f"{-1 * float(0):0.2f}".zfill(15)        # default '0'
        # total_record = f"{filler1}{sni_sales_type}{total_amount_with_tax}{total_amount_with_nontax}{tax_amount}{filler05}{total_amount_amt}{filler06}{sales_date}{sales_time}{positive_total}{negative_total}{filler12}{rounding_amount}{change_type}{change_amount}{gui_number}{member_card}{kadsim_card}{mommy_card}{refund_number}{refund_store_code}{refund_trans_date}{pre_booking_no}{refund_reason}{refund_description}{sales_tax_amount}{service_charge_amount}"
        total_record = f"{filler1}{sni_sales_type}{total_amount_with_nontax}{total_amount_with_nontax_able}{tax_amount}{filler05}{total_amount_paid}{filler06}{sales_date}{sales_time}{positive_total}{negative_total}{filler12}{rounding_amount}{change_type}{change_amount}{gui_number}{member_card}{kadsim_card}{mommy_card}{refund_number}{refund_store_code}{refund_trans_date}{pre_booking_no}{refund_reason}{refund_description}{sales_tax_amount}{service_charge_amount}"        
        master_code = f"{header}{total_record}\n"
        return master_code

    def payment_record(self, line, row, payment, is_duplicate):
        # Summary sales berdasarkan Payment Type berdasakan kode kartu
        # HEADER
        branch_code = line.branch_id.code
        if line.is_void == False and line.is_refund == False:
            sni_comment = str("0043").zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 
        else:
            if line.is_void == True:
                sni_comment = str("0045").zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 
            if line.is_refund == True:
                sni_comment = str("0044").zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 

        store_number = str(branch_code).ljust(4, '0')
        flags = "0".zfill(2) # default '0'
        pos_regis_num = str(line.session_id.config_id.code).zfill(3).ljust(6," ")
        # pos_trans_num = str(int(''.join(filter(str.isdigit, line.name)))).zfill(7)
        if line.pos_reference:
            if not is_duplicate:            
                receipt_no = str(line.pos_reference).replace("Order","")
                pos_trans_num = str(int(receipt_no)).zfill(8)
            else:
                receipt_no = str(line.pos_reference).replace("Order","")[-4:]
                order_ref = line.name.split('/')[1][-4:]
                pos_trans_num = order_ref + receipt_no                
        else:
            pos_trans_num = "0".zfill(8)
        
        # if line.pos_reference:
        #     receipt_no = str(line.pos_reference).replace("Order","")
        #     pos_trans_num = str(int(receipt_no)).zfill(8)
        # else:
        #     pos_trans_num = "0".zfill(8)

        sni_format = "C".zfill(1) # A-Item Record, B-Total Record, C-Payment Record, D-Cash Record, E-Tender Count Record

        header = f"{sni_comment}{store_number}{flags}{pos_regis_num}{pos_trans_num}{sni_format}"

        # TYPE C
        filler1 = "0" # default '0'
        if line.is_void == False and line.is_refund == False:
            sni_sales_type = str("0012").zfill(4) # 0012 - SALES, 0312 - RETURN
        else:
            sni_sales_type = str("0312").zfill(4) # 0012 - SALES, 0312 - RETURN

        filler = "0".zfill(3)                                       # default '0'
        payment_amount = f"{line.amount_paid:0.2f}".zfill(23)

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
            card_number = "".ljust(20, ' ')
        # MID
        if payment.merchant_id:
            merchant_code = str(payment.merchant_id).ljust(22, ' ')
        else:
            merchant_code = "".ljust(22, ' ')
        # approval code
        if payment.approval_code:
            approval_code = str(payment.approval_code)[:6].zfill(6)
        else:
            approval_code = "".ljust(6, " ")
        # TID
        if payment.terminal_id:
            terminal_id = str(payment.terminal_id)[:8].ljust(8, ' ')
        else:
            terminal_id = "".ljust(8, ' ')
        
        if payment.payment_method_id.credit_card_trace_no:
            trace_no = str(payment.payment_method_id.credit_card_trace_no).ljust(10, ' ')
        else:
            trace_no = "".ljust(10, ' ')

        actual_amt = f"{line.amount_paid:0.2f}".zfill(23)
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

    def payment_rounding(self, line, row):
        # Summary sales berdasarkan Payment Type berdasakan kode kartu
        # HEADER
        branch_code = line.branch_id.code
        if line.is_void == False and line.is_refund == False:
            sni_comment = str("0043").zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 
        else:
            if line.is_void == True:
                sni_comment = str("0045").zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 
            if line.is_refund == True:
                sni_comment = str("0044").zfill(4) # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 

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
        filler1 = "0" # default '0'
        if line.is_void == False and line.is_refund == False:
            sni_sales_type = str("0012").zfill(4) # 0012 - SALES, 0312 - RETURN
        else:
            sni_sales_type = str("0312").zfill(4) # 0012 - SALES, 0312 - RETURN

        filler = "0".zfill(3)                                       # default '0'
        if line.is_void == False:
            rounding_amount = line.amount_total - line.amount_paid
        else:
            rounding_amount = line.amount_total - line.amount_paid
        payment_amount = f"{rounding_amount:0.2f}".zfill(23)

        
        payment_type = "RND".zfill(3)

        pos_pay_type_code = "~R".ljust(8, ' ')
        # PAN        
        card_number = "".ljust(20, ' ')
        # MID
        merchant_code = "".ljust(22, ' ')
        # approval code
        approval_code = "".ljust(6, " ")
        # TID
        terminal_id = "".ljust(8, ' ')
                
        trace_no = "".ljust(10, ' ')

        actual_amt = f"{rounding_amount:0.2f}".zfill(23)
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

    def cash_record(self, sni_comment, type_d):
        # Summary sales berdasarkan sales bertipe cash, dan inputan cashier berdasarkan perhitungan fisik cash drawer
        # HEADER
        
        #branch_code = line.branch_id.code
        # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 
        sni_comment = sni_comment.zfill(4) 
 
        store_number = str(type_d['branch_code']).ljust(4, '0')
        flags = "0".zfill(2)  # default '0'
        pos_regis_num = type_d['pos_config_code'].zfill(3).ljust(6," ")
        receipt_no = type_d['pos_ref'].replace("Order","")
        pos_trans_num = str(int(receipt_no)).zfill(8)
        # pos_trans_num = str(int(''.join(filter(str.isdigit, line.name)))).zfill(7)
        # if line.pos_reference:
        #     receipt_no = str(line.pos_reference).replace("Order","")
        #     pos_trans_num = str(int(receipt_no)).zfill(8)
        # else:
        #     pos_trans_num = "0".zfill(8)
        
        sni_format = "D".zfill(1) # A-Item Record, B-Total Record, C-Payment Record, D-Cash Record, E-Tender Count Record

        header = f'{sni_comment}{store_number}{flags}{pos_regis_num}{pos_trans_num}{sni_format}'

        # TYPE D
        filler1 = "0"                                           # default '0'
        cashier_id = type_d['cashier_id'].zfill(9)
        loan_amount = f"{float('0'):0.2f}".zfill(23)
        middle_collec_amount = f"{float('0'):0.2f}".zfill(23)
        cash_sales = f"{float(type_d['cash_sales']):0.2f}".zfill(23)             # default '0'
        filler2 = "0000000000"                                                   # default '0'
        cash_count = f"{float(type_d['cash_count']):0.2f}".zfill(13)             # default '0'

        cash_record = f"{filler1}{cashier_id}{loan_amount}{middle_collec_amount}{cash_sales}{filler2}{cash_count}"
        master_record = f'{header}{cash_record}\n'

        return master_record
    
    def tender_count_record(self, sni_comment, type_e):
        # Summary sales berdasarkan payment type
        # HEADER
        
        # 0043-Valid Sales, 0000-Total Record, 0044-Refund, 0045-Void 
        sni_comment = sni_comment.zfill(4) 

        store_number = type_e['branch_code'].ljust(4, '0')
        flags = "0".zfill(2)
        pos_regis_num = type_e['pos_config_code'].zfill(3).ljust(6," ")
        receipt_no = type_e['pos_ref'].replace("Order","")
        pos_trans_num = str(int(receipt_no)).zfill(8)

        # A-Item Record, B-Total Record, C-Payment Record, D-Cash Record, E-Tender Count Record
        sni_format = "E".zfill(1) 

        header = f'{sni_comment}{store_number}{flags}{pos_regis_num}{pos_trans_num}{sni_format}'

        # TYPE E
        filler1 = "0"                                   # default '0'
        if sni_comment == "0043":
            sni_sales_type = str("0012").zfill(4)   # 0012 - SALES, 0312 - RETURN
        elif sni_comment == "0044":
            sni_sales_type = str("0312").zfill(4)   # 0012 - SALES, 0312 - RETURN
        else:
            str("0000").zfill(4)
            
        pos_id = str(type_e['pos_config_code']).zfill(3)

        if type_e['payment_code']:
            payment_type = str(type_e['payment_code']).ljust(3," ")
        else:
            payment_type = "".ljust(3," ")

        if type_e['payment_sales']:
            payment_sales = f"{float(type_e['payment_sales']):0.2f}".zfill(23)
        else:
            payment_sales = f"{float('0'):0.2f}".zfill(23)

        if type_e['payment_count']:
            payment_count = f"{float(type_e['payment_count']):0.2f}".zfill(23)
        else:
            payment_count = f"{float('0'):0.2f}".zfill(23)

        tender_count_record = f'{filler1}{sni_sales_type}{pos_id}{payment_type}{payment_sales}{payment_count}'
        master_record = f'{header}{tender_count_record}\n'

        return master_record

    def summary_sales_all(self, type_t):
        # Summary sales keseluruhan data
        # HEADER
        sni_comment = "0043" 
        store_number = type_t['branch_code'].ljust(4, '0')
        flags = "0".zfill(2)      # default '0'
        pos_regis_num = type_t['pos_config_code'].zfill(3).ljust(6," ")
        receipt_no = type_t['pos_ref'].replace("Order","")
        pos_trans_num = str(int(receipt_no)).zfill(8)
        sni_format = "T".zfill(1) # A-Item Record, B-Total Record, C-Payment Record, D-Cash Record, E-Tender Count Record

        header = f'{sni_comment}{store_number}{flags}{pos_regis_num}{pos_trans_num}{sni_format}'

        # TYPE T
        filler1 = "0"                                           # default '0'
        line_count = str(type_t['line_count']).zfill(8)
        diff_sales = type_t['sales_amount'] - type_t['return_amount']
        total_sales_amount = f"{diff_sales:0.2f}".zfill(23)
        total_redeem_coupon = "0".zfill(8)
        value_redeem_coupon = f"{float('0'):0.2f}".zfill(23)
        sales_rcpt_count = str(type_t['sales_count']).zfill(8)
        return_rcpt_count = str(type_t['return_count']).zfill(8)        
        rounding_amt = "-" + f"{type_t['rounding_amount']:0.2f}".zfill(9)

        summary_sales_all = f"{filler1}{line_count}{total_sales_amount}{total_redeem_coupon}{value_redeem_coupon}{sales_rcpt_count}{return_rcpt_count}{rounding_amt}"
        master_record = f"{header}{summary_sales_all}\n"

        return master_record
    
    def file_name(self, lastnumb, date_request):
        #date_time = datetime.now()
        date_time = date_request + relativedelta(hours=7)
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
        RR = "01"
        filename = "S{}{}{}{}".format(Y, M, D, RR).upper()
        return filename.upper()

    def get_pos_order_upload(self, date_time=False):
        # Define variable
        s_file_type_a = []

        if not date_time:
            date_time = datetime.now() # + timedelta(days=-1)
        else:
            date_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
        
        str_start_date = str(date_time.year)+ "-" + str(date_time.month).zfill(2) + "-" + str(date_time.day).zfill(2) + " " + "00:00:00"
        start_date_time = datetime.strptime(str_start_date, "%Y-%m-%d %H:%M:%S") - relativedelta(hours=7)
        #start_date_time = datetime.strptime(str_start_date, "%Y-%m-%d %H:%M:%S") + timedelta(hours-7)
        # - relativedelta(hours=7)

        str_end_date = str(date_time.year) + "-" + str(date_time.month).zfill(2) + "-" + str(date_time.day).zfill(2) + " " + "23:59:59"
        end_date_time = datetime.strptime(str_end_date, "%Y-%m-%d %H:%M:%S") - relativedelta(hours=7)
        # - relativedelta(hours=7)

        sqlgroup="""
            SELECT a.branch_id, b.code as branch_code FROM pos_order a
            LEFT JOIN res_branch b ON a.branch_id = b.id
            WHERE a.create_date BETWEEN '{}' AND '{}'
            GROUP BY a.branch_id, b.code
        """.format(start_date_time, end_date_time) # .format(start_date_time, end_date_time) WHERE create_date BETWEEN '{}' AND '{}'        
        self.env.cr.execute(sqlgroup)
        groups = self.env.cr.dictfetchall()

        if len(groups) > 0:
            for group in groups:
                output = StringIO()
                
                max_row = 0
                total_refund = 0.0
                total_sales = 0.0
                total_t = 0.0
                sales_rcpt_c = 0
                return_rcpt_c = 0
                cash_count = 0
                total_cash = 0.0
                #Get Duplicate Row
                strSQL_duplicate = """SELECT a.pos_reference
                            FROM pos_order a 
                            LEFT JOIN pos_session b ON a.session_id=b.id
                            LEFT JOIN pos_config c ON b.config_id=c.id
                            WHERE c.res_branch_id={} AND a.date_order BETWEEN '{}' and '{}'
                            GROUP BY a.pos_reference
                            HAVING (COUNT(a.pos_reference) > 1)""".format(group['branch_id'], start_date_time, end_date_time)
                self.env.cr.execute(strSQL_duplicate)
                duplicate_receipts = self.env.cr.fetchall()
                #_logger.info(duplicate_receipts)
                duplicate_data = []            
                for row in duplicate_receipts:
                    _logger.info(row[0])
                    duplicate_data.append(row[0])

                #TYPE A
                domain = [
                    ('branch_id','=', group['branch_id']), 
                    ('date_order','>=', start_date_time),
                    ('date_order','<=', end_date_time)
                ] # , ('create_date','>=', start_date_time), ('create_date','<=', end_date_time)                
                orders = self.env['pos.order'].search(domain, order='id asc')

                # TYPE A, TYPE B AND TYPE C                
                is_duplicate = False
                for order in orders:
                    # TYPE A
                    i = 0                            
                    is_duplicate = False
                    if order.pos_reference in duplicate_data:
                        is_duplicate = True

                    for row in order.lines:                                                                                            
                        item_record = self.item_record(order, row, is_duplicate) # TYPE A                        
                        output.write(item_record)                        
                        #Prepare Type A
                        # s_file_type_a.append(
                        #     ( 
                        #         0,
                        #         0,
                        #         {
                        #             'h001': item_record[0:4], 'h002':item_record[4:8], 'h003': item_record[8:], 'h004':, 'h005':, 'h006':,
                        #             'a001':, 'a002':, 'a003':, 'h004':, 'a005':, 'a006':,'a007':, 'a008':, 'a009':, 'a010':,
                        #             'a011':, 'a012':, 'a013':, 'a014':, 'a015':, 'a016':,'a017':, 'a018':, 'a019':, 'a020':,
                        #             'a021':, 'a022':, 'a023':, 'a024':, 'a025':, 'a026':,'a027':, 'a028':, 'a029':, 'a030':,
                        #             'a031':, 'a032':, 'a033':, 'a034':, 'a035':, 'a036':,'a037':, 'a038':, 'a039':, 'a040':,
                        #             'a041':, 'a042':, 'a043':
                        #         }
                        #     )
                        # )
                        # _logger.info(item_record)
                        max_row += 1
                        #_logger.info(max_row)
                        if row.price_subtotal_incl < 0.0:
                            total_refund += row.price_subtotal_incl
                        else:
                            total_sales += row.price_subtotal_incl                             
                    row = ""
                    # TYPE B
                    total_record = self.total_record(order, row, is_duplicate)
                    output.write(total_record)                    
                    
                    # _logger.info(total_record)
                    
                    max_row += 1                    
                    
                    # TYPE C
                    for payment in order.payment_ids:
                        payment_record = self.payment_record(order, row, payment, is_duplicate) # TYPE C
                        output.write(payment_record)
                        # _logger.info(payment_record)
                        if order.is_void == False:
                            if order.amount_paid < order.amount_total:
                                #_logger.info('Rounding')
                                payment_record = self.payment_rounding(order, row)
                                output.write(payment_record)
                                # _logger.info(payment_record)
                        else:
                            if order.amount_paid > order.amount_total:
                                #_logger.info('Rounding')
                                payment_record = self.payment_rounding(order, row)
                                output.write(payment_record)
                                # _logger.info(payment_record)

                        max_row += 1
                    
                    

                    if order.is_refunded == False:
                        sales_rcpt_c += 1
                    else:
                        return_rcpt_c += 1

                    for rec in order.payment_ids:
                        if rec.payment_method_id.code == "CSH":
                            total_cash += rec.amount
                            cash_count += 1

                    is_duplicate = False
                    
                # TYPE D
                # TYPE D - VALID SALES - 0043
                strSQL_type_d = """
                    SELECT d.branch_id as branch_id, f.code as branch_code, 
                           d.config_id as pos_config_id, g.code as pos_config_code,
                           max(c.pos_reference) as pos_ref, e.login as cashier_id, b.code as payment_code, 
                           sum(a.amount) as cash_sales, count(*) as cash_count 
                    FROM pos_payment a
                    LEFT JOIN pos_payment_method b ON b.id  = a.payment_method_id 
                    LEFT JOIN pos_order c on c.id = a.pos_order_id
                    LEFT JOIN pos_session d on d.id = c.session_id
                    LEFT JOIN res_users e on e.id = d.user_id
                    LEFT JOIN res_branch f on f.id = d.branch_id
                    LEFT JOIN pos_config g on g.id = d.config_id
                    LEFT JOIN res_partner h on h.id = e.partner_id
                    WHERE d.branch_id = '{}' AND b.code = '{}' AND c.date_order BETWEEN '{}' AND '{}'
                    GROUP BY d.branch_id, f.code, d.config_id, g.code, e.login, b.code ORDER BY b.code
                """.format(group['branch_id'], 'CSH',start_date_time, end_date_time)
                # _logger.info(strSQL_type_d)
                self.env.cr.execute(strSQL_type_d)
                data_type_d = self.env.cr.dictfetchall()
                for type_d in data_type_d:
                    cash_record = self.cash_record("0043", type_d)
                    output.write(cash_record)
                    # _logger.info(cash_record)
                    max_row += 1

                # TYPE D - REFUND - 0044
                # strSQL_type_d = """
                #     SELECT d.branch_id as branch_id, f.code as branch_code, 
                #            d.config_id as pos_config_id, g.code as pos_config_code, 
                #            max(c.pos_reference) as pos_ref, h.name as cashier_id, b.code as payment_code, 
                #            sum(a.amount) as cash_sales, count(*) as cash_count 
                #     FROM pos_payment a
                #     LEFT JOIN pos_payment_method b ON b.id  = a.payment_method_id 
                #     LEFT JOIN pos_order c on c.id = a.pos_order_id
                #     LEFT JOIN pos_session d on d.id = c.session_id
                #     LEFT JOIN res_users e on e.id = d.user_id
                #     LEFT JOIN res_branch f on f.id = d.branch_id
                #     LEFT JOIN pos_config g on g.id = d.config_id
                #     LEFT JOIN res_partner h on h.id = e.partner_id
                #     WHERE a.amount < 0 AND d.branch_id = '{}' AND b.code = '{}' AND c.date_order BETWEEN '{}' AND '{}'
                #     GROUP BY d.branch_id, f.code, d.config_id, g.code, h.name, b.code ORDER BY b.code
                # """.format(group['branch_id'], 'CSH',start_date_time, end_date_time)
                # _logger.info(strSQL_type_d)
                # self.env.cr.execute(strSQL_type_d)
                # data_type_d = self.env.cr.dictfetchall()
                # for type_d in data_type_d:
                #     cash_record = self.cash_record("0044", type_d)
                #     output.write(cash_record)
                #     _logger.info(cash_record)
                #     max_row += 1

                # TYPE E
                # TYPE E - VALID SALES - 0043
                strSql_type_e = """
                    SELECT d.branch_id as branch_id, f.code as branch_code, 
                           d.config_id as pos_config_id, g.code  as pos_config_code, 
                           max(c.pos_reference) as pos_ref, e.login as cashier_id, b.code as payment_code, 
                           sum(a.amount) as payment_sales, count(*) as payment_count 
                    FROM pos_payment a
                    LEFT JOIN pos_payment_method b ON b.id  = a.payment_method_id 
                    LEFT JOIN pos_order c on c.id = a.pos_order_id
                    LEFT JOIN pos_session d on d.id = c.session_id
                    LEFT JOIN res_users e on e.id = d.user_id
                    LEFT JOIN res_branch f on f.id = d.branch_id
                    LEFT JOIN pos_config g on g.id = d.config_id
                    WHERE d.branch_id = '{}' AND c.date_order BETWEEN '{}' AND '{}'
                    GROUP BY d.branch_id, f.code, d.config_id, g.code, e.login, b.code ORDER BY b.code
                """.format(group['branch_id'],start_date_time, end_date_time)
                # _logger.info(strSql_type_e)
                self.env.cr.execute(strSql_type_e)
                data_type_e = self.env.cr.dictfetchall()
                for type_e in data_type_e:
                    tender_count_record = self.tender_count_record("0043", type_e) # TYPE E
                    output.write(tender_count_record)
                    # _logger.info('tender_count_record')
                    # _logger.info(tender_count_record)
                    max_row += 1
                total_sales_refund = total_sales + total_refund   

                # # TYPE E
                # # TYPE - REFUND - 0044
                # strSql_type_e = """
                #     SELECT d.branch_id as branch_id, f.code as branch_code, 
                #            d.config_id as pos_config_id, g.code as pos_config_code, 
                #            max(c.pos_reference) as pos_ref, e.login as cashier_id, b.code as payment_code, 
                #            sum(a.amount) as payment_sales, count(*) as payment_count 
                #     FROM pos_payment a
                #     LEFT JOIN pos_payment_method b ON b.id  = a.payment_method_id 
                #     LEFT JOIN pos_order c on c.id = a.pos_order_id
                #     LEFT JOIN pos_session d on d.id = c.session_id
                #     LEFT JOIN res_users e on e.id = d.user_id
                #     LEFT JOIN res_branch f on f.id = d.branch_id
                #     LEFT JOIN pos_config g on g.id = d.config_id
                #     WHERE a.amount < 0 AND d.branch_id = '{}' AND c.date_order BETWEEN '{}' AND '{}'
                #     GROUP BY d.branch_id, f.code, d.config_id, g.code, e.login, b.code ORDER BY b.code
                # """.format(group['branch_id'],start_date_time, end_date_time)
                # _logger.info(strSql_type_e)
                # self.env.cr.execute(strSql_type_e)
                # data_type_e = self.env.cr.dictfetchall()
                # for type_e in data_type_e:
                #     tender_count_record = self.tender_count_record("0044", type_e) # TYPE E
                #     output.write(tender_count_record)
                #     _logger.info('tender_count_record')
                #     _logger.info(tender_count_record)
                #     max_row += 1
                total_sales_refund = total_sales + total_refund   

                #TYPE T
                sales_all = {
                    'line_count': max_row
                }
                # TYPE T - VALID SALES
                strSql_type_t = """
                SELECT d.branch_id as branch_id, f.code as branch_code,
                           max(g.code) as pos_config_code ,
                           max(c.pos_reference) as pos_ref,
                           sum(c.amount_total) as sales_amount,
                           sum(c.amount_total - c.amount_paid) as rounding_amount,
                           count(*) as sales_count
                    FROM pos_order c
                    LEFT JOIN pos_session d on d.id = c.session_id
                    LEFT JOIN res_users e on e.id = d.user_id
                    LEFT JOIN res_branch f on f.id = d.branch_id
                    LEFT JOIN pos_config g on g.id = d.config_id
                    WHERE g.res_branch_id = '{}' AND c.date_order BETWEEN '{}' AND '{}'
                    GROUP BY d.branch_id, f.code ORDER BY f.code
                """.format(group['branch_id'],start_date_time, end_date_time)

                # strSql_type_t = """
                #     SELECT d.branch_id as branch_id, f.code as branch_code,                            
                #            d.config_id as pos_config_id, g.code as pos_config_code, 
                #            max(c.pos_reference) as pos_ref,
                #            sum(c.amount_paid) as sales_amount, 
                #            sum(c.amount_total - c.amount_paid) as rounding_amount,
                #            count(*) as sales_count
                #     FROM pos_order c                    
                #     LEFT JOIN pos_session d on d.id = c.session_id
                #     LEFT JOIN res_users e on e.id = d.user_id
                #     LEFT JOIN res_branch f on f.id = d.branch_id
                #     LEFT JOIN pos_config g on g.id = d.config_id
                #     WHERE g.res_branch_id = '{}' AND c.date_order BETWEEN '{}' AND '{}'
                #     GROUP BY d.branch_id, f.code, d.config_id, g.code ORDER BY f.code
                # """.format(group['branch_id'],start_date_time, end_date_time)
                
                # _logger.info(strSql_type_t)
                self.env.cr.execute(strSql_type_t)
                data_type_t = self.env.cr.dictfetchall()
                for type_t in data_type_t:
                    sales_all.update({
                        'branch_code': type_t['branch_code'],
                        'pos_config_code': type_t['pos_config_code'],
                        'pos_ref': type_t['pos_ref'],
                        'sales_amount': type_t['sales_amount'],
                        'sales_count': type_t['sales_count'],
                        'rounding_amount': type_t['rounding_amount'],
                        'return_amount': 0.0,
                        'return_count': 0
                    })   
                    total_t = total_t + type_t['sales_amount']

                summary_sales_all = self.summary_sales_all(sales_all)               
                output.write(summary_sales_all)
                # _logger.info(summary_sales_all)

                #GENERATE FILE
                store = str(group['branch_code'])
                master_code_file = base64.encodebytes(output.getvalue().encode('utf-8'))
                datenow = datetime.now().date()
                # trans_count = self.env['pos.order.file'].search_count([('date', '=', datenow), ('flag_number','=', store)])
                sql="""select count(*) from pos_order_file where DATE(date)= '{}' and flag_number='{}'""".format(datenow, store)
                self.env.cr.execute(sql)
                trans_count = self.env.cr.dictfetchall()
                for total_count in trans_count:
                    lastnumb = total_count['count']
                    # _logger.info("LASTNUMBER")
                    # _logger.info(trans_count)
                    # _logger.info(lastnumb)
                numb = 0
                if lastnumb == 12 or lastnumb == 0: 
                    numb = 1
                else:
                    numb = lastnumb+1
                numb = 1
                filename = self.file_name(numb, start_date_time)

                # _logger.info(store)
                filename = f'{filename}{store[0]}.{store[1:]}'
                #_logger.info(filename)
                # output.close()
                vals = {
                    'file': master_code_file,
                    'filename': filename.upper(),
                    'flag_number': store,
                    'type_a_total': total_sales + total_refund,
                    'type_t_total': total_t
                }
                #_logger.info(vals)                
                self.create(vals)
                _logger.info(total_sales)
                _logger.info(total_refund)
                _logger.info(total_sales + total_refund)
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

    type_a_total = fields.Float('Total Type A')
    type_t_total = fields.Float('Total Type T')

    # sales_file_a_ids = fields.One2many('pos.order.file','pos_order_file_id','Type A')
    
    @api.model
    def create(self, vals):
        res = super(pos_order_file, self).create(vals)
        res.action_save_to_directory()


# class SalesFileA(models.Model):
#     _name = 'sales.file.a'

#     pos_order_file_id = fields.Many2one('pos.order.file', 'Order File #')
#     h001 = fields.Char('H001')
#     h002 = fields.Char('H001')
#     h003 = fields.Char('H001')
#     h004 = fields.Char('H001')
#     h005 = fields.Char('H001')
#     h006 = fields.Char('H001')
#     a001 = fields.Char('A001')
#     a002 = fields.Char('A002')
#     a003 = fields.Char('A003')
#     a004 = fields.Char('A004')
#     a005 = fields.Char('A005')
#     a006 = fields.Char('A006')
#     a007 = fields.Char('A007')
#     a008 = fields.Char('A008')
#     a009 = fields.Char('A009')
#     a010 = fields.Char('A010')
#     a011 = fields.Char('A011')
#     a012 = fields.Char('A012')
#     a013 = fields.Char('A013')
#     a014 = fields.Char('A014')
#     a015 = fields.Char('A015')
#     a016 = fields.Char('A016')
#     a017 = fields.Char('A017')
#     a018 = fields.Char('A018')
#     a019 = fields.Char('A019')
#     a020 = fields.Char('A020')
#     a021 = fields.Char('A021')
#     a022 = fields.Char('A022')
#     a023 = fields.Char('A023')
#     a024 = fields.Char('A024')
#     a025 = fields.Char('A025')
#     a026 = fields.Char('A026')
#     a027 = fields.Char('A027')
#     a028 = fields.Char('A028')
#     a029 = fields.Char('A029')
#     a030 = fields.Char('A030')
#     a031 = fields.Char('A031')
#     a032 = fields.Char('A032')
#     a033 = fields.Char('A033')
#     a034 = fields.Char('A034')
#     a035 = fields.Char('A035')
#     a036 = fields.Char('A036')
#     a037 = fields.Char('A037')
#     a038 = fields.Char('A038')
#     a039 = fields.Char('A039')
#     a040 = fields.Char('A040')
#     a041 = fields.Char('A041')
#     a042 = fields.Char('A042')
#     a043 = fields.Char('A043')