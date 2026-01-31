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
from datetime import datetime, date, timedelta
import uuid
import requests
from requests.auth import HTTPBasicAuth
import logging
_logger = logging.getLogger(__name__)


class PricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    def _cron_clean_expired_pricelist_from_couchdb(self):
        """
        Scheduled action to clean expired pricelist items from CouchDB.
        This method will be called by cron to clean up expired pricelists.
        """
        _logger.info("Starting scheduled cleanup of expired pricelist items from CouchDB")
        
        # Get retention days from system parameter (default: -7 days)
        retention_days = int(self.env['ir.config_parameter'].sudo().get_param(
            'weha_smart_pos.pricelist_retention_days', '-7'
        ))
        
        # Get all branches
        branches = self.env['res.branch'].search([])
        
        for branch in branches:
            try:
                _logger.info(f"Processing branch: {branch.name} (ID: {branch.id})")
                self.clean_expired_pricelist_items_by_branch(branch, retention_days)
            except Exception as e:
                _logger.error(f"Error cleaning expired pricelist for branch {branch.name}: {str(e)}")
                continue
        
        _logger.info("Completed scheduled cleanup of expired pricelist items from CouchDB")

    def clean_expired_pricelist_items_by_branch(self, branch, retention_days=-7):
        """
        Clean expired pricelist items from CouchDB for a specific branch.
        
        :param branch: res.branch record
        :param retention_days: Number of days to retain after date_end (negative value)
        """
        if not branch.couchdb_server_url or not branch.couchdb_product_pricelist_items:
            _logger.warning(f"Branch {branch.name} does not have CouchDB configuration. Skipping.")
            return

        auth = HTTPBasicAuth('admin', 'pelang1')
        headers = {
            'Content-Type': 'application/json'
        }

        # Calculate retention date
        current_date_time = datetime.now()
        retain_date_time = current_date_time + timedelta(days=retention_days)
        retain_date_str = retain_date_time.strftime('%Y-%m-%d')

        _logger.info(f"Cleaning pricelist items with date_end before: {retain_date_str}")

        # Query CouchDB for expired pricelist items
        find_url = f'{branch.couchdb_server_url}/{branch.couchdb_product_pricelist_items}/_find'
        
        query = {
            "selector": {
                "date_end": {
                    "$lt": retain_date_str
                }
            },
            "fields": ["_id", "_rev", "id", "date_start", "date_end"],
            "limit": 1000
        }

        try:
            response = requests.post(find_url, auth=auth, headers=headers, 
                                    data=json.dumps(query), verify=False)
            
            if response.status_code == 200:
                response_json = response.json()
                docs = response_json.get("docs", [])
                
                _logger.info(f"Found {len(docs)} expired pricelist items in CouchDB for branch {branch.name}")
                
                deleted_count = 0
                for doc in docs:
                    try:
                        doc_id = doc['_id']
                        doc_rev = doc['_rev']
                        
                        # Delete from CouchDB
                        delete_url = f'{branch.couchdb_server_url}/{branch.couchdb_product_pricelist_items}/{doc_id}?rev={doc_rev}'
                        delete_response = requests.delete(delete_url, auth=auth, headers=headers, verify=False)
                        
                        if delete_response.status_code in (200, 201):
                            deleted_count += 1
                            _logger.info(f"Deleted expired pricelist item: {doc_id} (date_end: {doc.get('date_end')})")
                        else:
                            _logger.warning(f"Failed to delete pricelist item {doc_id}: Status {delete_response.status_code}")
                    
                    except Exception as e:
                        _logger.error(f"Error deleting document {doc.get('_id')}: {str(e)}")
                        continue
                
                _logger.info(f"Successfully deleted {deleted_count} expired pricelist items from CouchDB for branch {branch.name}")
            
            else:
                _logger.error(f"Failed to query CouchDB: Status {response.status_code}, Response: {response.text}")
        
        except requests.exceptions.RequestException as e:
            _logger.error(f"Request exception while cleaning expired pricelists for branch {branch.name}: {str(e)}")
        except Exception as e:
            _logger.error(f"Unexpected error while cleaning expired pricelists for branch {branch.name}: {str(e)}")

    def action_manual_clean_expired_pricelist(self):
        """
        Manual action to clean expired pricelist items from CouchDB.
        Can be called from a button or wizard.
        """
        retention_days = int(self.env['ir.config_parameter'].sudo().get_param(
            'weha_smart_pos.pricelist_retention_days', '-7'
        ))
        
        branches = self.env['res.branch'].search([])
        
        for branch in branches:
            try:
                self.clean_expired_pricelist_items_by_branch(branch, retention_days)
            except Exception as e:
                _logger.error(f"Error cleaning expired pricelist for branch {branch.name}: {str(e)}")
                continue
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Expired pricelist items have been cleaned from CouchDB.'),
                'type': 'success',
                'sticky': False,
            }
        }
