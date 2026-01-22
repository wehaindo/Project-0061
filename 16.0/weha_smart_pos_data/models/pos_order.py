# -*- coding: utf-8 -*-
#################################################################################
# Author      : WEHA Consultant (<www.weha-id.com>)
# Copyright(c): 2015-Present WEHA Consultant.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import simplejson as json
from datetime import datetime, date
import uuid
import requests
from requests.auth import HTTPBasicAuth
from random import randrange
import logging
_logger = logging.getLogger(__name__)



class PosOrder(models.Model):
    _inherit = 'pos.order'


    def create_from_ui_couchdb(self, orders, draft=False):
        
        # order_ids = []
        # existing_order = False
        # for order in orders:
        #     order_ids.append(self._process_order(order, draft, existing_order))

        # return self.env['pos.order'].search_read(domain=[('id', 'in', order_ids)], fields=['id', 'pos_reference', 'account_move'], load=False)
    
        order_names = [order['data']['name'] for order in orders]
        sync_token = randrange(100000000)  # Use to differentiate 2 parallels calls to this function in the logs
        _logger.info("Start PoS synchronisation #%d for PoS orders references: %s (draft: %s)", sync_token, order_names, draft)
        order_ids = []
        for order in orders:
            order_accesss_token = order['data']['access_token']
            existing_draft_order = None

            if 'access_token' in order['data'] and order['data']['access_token']:
                # if the server id exists, it must only search based on the id
                existing_draft_order = self.env['pos.order'].search(['&', ('access_token', '=', order['data']['access_toke']), ('state', '=', 'draft')], limit=1)

                # if there is no draft order, skip processing this order
                if not existing_draft_order:
                    continue

            # if not existing_draft_order:
            #     existing_draft_order = self.env['pos.order'].search(['&', ('pos_reference', '=', order_name), ('state', '=', 'draft')], limit=1)

            try:
                if existing_draft_order:
                    order_ids.append(self._process_order(order, draft, existing_draft_order))
                else:
                    existing_orders = self.env['pos.order'].search([('access_token', '=', order_accesss_token)])
                    if all(not self._is_the_same_order(order['data'], existing_order) for existing_order in existing_orders):
                        order_ids.append(self._process_order(order, draft, False))
            except Exception as e:
                _logger.exception("An error occurred when processing the PoS order %s", order_accesss_token)
                
        res = self.env['pos.order'].search_read(domain=[('id', 'in', order_ids)], fields=['id', 'pos_reference', 'account_move'], load=False)
        _logger.info("Finish PoS synchronisation #%d with result: %s", sync_token, res)
        return res

