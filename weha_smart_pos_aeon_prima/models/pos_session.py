# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, _
from odoo.addons.weha_smart_pos_aeon_prima.libs.dashboard_client import DashboardClient
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timezone
# from pytz import timezone
import pytz



import logging
_logger = logging.getLogger(__name__)



class PosSession(models.Model):
    _inherit = 'pos.session'
	
    def is_utc(self, dt):
        return dt.tzinfo is not None and dt.tzinfo == timezone.utc

    def get_prima_current_datetime(self):
        local_tz = pytz.timezone('Asia/Jakarta')
        current_date = datetime.now()
        return current_date.astimezone(local_tz).strftime("%d-%m-%Y %H:%M:%S")

    def get_prima_opened_date(self):
        local_tz = pytz.timezone('Asia/Jakarta')
        return datetime.strptime(str(self.start_at), "%Y-%m-%d %H:%M:%S").astimezone(local_tz).strftime("%d-%m-%Y %H:%M:%S")
        
    def get_prima_closed_date(self):
        local_tz = pytz.timezone('Asia/Jakarta')
        if self.stop_at:
            return datetime.strptime(str(self.stop_at), "%Y-%m-%d %H:%M:%S").astimezone(local_tz).strftime("%d-%m-%Y %H:%M:%S")

    def action_prima_session_z_report(self):
        doc_ids = self.env.context.get('active_ids')
        data = {}
        return self.env.ref('weha_smart_pos_aeon_prima.action_report_prima_session_z').report_action(docids=doc_ids, data=data, config=False)

    def get_pos_merchant_id(self):
        return self.config_id.prima_merchant_id
    
    def get_pos_terminal_id(self):
        return self.config_id.prima_terminal_id

    #def get_prima_payment_detail_data(self, date_start, date_end, merchant_id, terminal_id):
    def get_prima_payment_detail_data(self):
        try:
            local_tz = pytz.timezone('Asia/Jakarta')
            payment_details = []
            dashboard_client = DashboardClient()
            # response = dashboard_client.transaction("2024-08-01","2024-09-12","998224042354469","AEON0001")                        
            local_start_date = self.start_at.replace(tzinfo=pytz.utc).astimezone(local_tz)   
            start_date  = local_start_date.strftime('%Y-%m-%d') + "T" +  local_start_date.strftime('%H:%M:%S')            
            end_date = ''
            if self.stop_at:
                local_end_date = self.stop_at.replace(tzinfo=pytz.utc).astimezone(local_tz)   
                end_date = local_end_date.strftime('%Y-%m-%d') + "T" + local_end_date.strftime('%H:%M:%S')
            else:
                current_date = datetime.now(timezone.utc)
                # stop_at = current_date.replace(tzinfo=pytz.utc).astimezone(local_tz)
                stop_at = current_date.astimezone(local_tz)
                _logger.info(stop_at)                           
                # if self.is_utc(current_date):
                #     _logger.info('is_utc')
                #     stop_at = current_date.replace(tzinfo=pytz.utc).astimezone(local_tz)
                # else:
                #     _logger.info('not is_utc')
                #     stop_at = current_date    
                
                end_date = stop_at.strftime('%Y-%m-%d') + "T" + stop_at.strftime('%H:%M:%S')
            response = dashboard_client.transaction(start_date, end_date, self.get_pos_merchant_id(),self.get_pos_terminal_id())
            _logger.info(response)
            if response['error'] == False:
                payments = response['data']
                for payment in payments: 
                    payment_date = datetime.strptime(payment['CREATED_DATE'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    local_payment_date =  payment_date.replace(tzinfo=pytz.utc).astimezone(local_tz)   
                    payment_detail = {
                        'payment_date': local_payment_date.strftime('%H:%M:%S'),
                        'status': payment['TRANSACTION_STATUS'],
                        'pan': payment['CPAN'],
                        'amount': payment['AMOUNT'],
                        'rrn': payment['RRN']
                    }
                    payment_details.append(payment_detail)
                return payment_details
            else:
                # raise ValidationError(_(response['message']))
                return []
        except Exception as e:
            _logger.info(e)            
            # raise ValidationError(_(e))
            return []

    def _loader_params_pos_payment_method(self):
        result = super()._loader_params_pos_payment_method()    
        return result

