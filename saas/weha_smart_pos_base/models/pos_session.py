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
import logging

_logger = logging.getLogger(__name__)

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        if self.config_id.use_store_access_rights:
            loaded_data['res.users.supervisor.by.id'] = {supervisor['id']: supervisor for supervisor in loaded_data['res.users.supervisor']}
            loaded_data['res.users.supervisor.by.rfid'] = {supervisor['rfid']: supervisor for supervisor in loaded_data['res.users.supervisor']}

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        if self.config_id.use_store_access_rights:
            new_model = 'res.users.supervisor'
            if new_model not in result:
                result.append(new_model)
        return result

    def _loader_params_res_users_supervisor(self):
        if len(self.config_id.supervisor_ids) > 0:
            domain = [('id', 'in', self.config_id.supervisor_ids.ids)]
        else: 
            domain = []
        return {'search_params': {'domain': domain, 'fields': ['name', 'id', 'rfid'], 'load': False}}

    def _get_pos_ui_res_users_supervisor(self, params):
        supervisor_ids = self.env['res.users'].search_read(**params['search_params'])
        return supervisor_ids