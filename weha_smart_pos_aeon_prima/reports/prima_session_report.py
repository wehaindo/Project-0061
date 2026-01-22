# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import logging
from datetime import timedelta,date,datetime
from functools import partial

import psycopg2
import pytz

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)

class PrimaSessionReport(models.TransientModel):

	_name='prima.session.report'
	_description = "Prima Session Report"
	
	def generate_datas(self, pos_session_id, date_start, date_end, merchant_id, terminal_id):
		prima_payment_details = pos_session_id.get_prima_payment_detail_data(date_start, date_end, merchant_id, terminal_id)			
		data = {
			'current_datetime': pos_session_id.get_current_datetime(),
			'user_name': pos_session_id.user_id.name,
			'pos_name': pos_session_id.get_pos_name(),
			'session_name': pos_session_id.name,
			'merchant_id': pos_session_id.get_pos_merchant_id(),
			'terminal_id': pos_session_id.get_pos_terminal_id(),
			'opening_date': pos_session_id.get_opened_date(),
			'closed_date': pos_session_id.get_closed_date(),
			'status': pos_session_id.state,
			'prima_payment_details': prima_payment_details
		}
		return data

