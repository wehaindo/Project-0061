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

class PosConfig(models.Model):
    _inherit = 'pos.config'

    def open_mobile(self):
        """Open the pos interface with config_id as an extra argument.
        In vanilla PoS each user can only have one active session, therefore it was not needed to pass the config_id
        on opening a session. It is also possible to login to sessions created by other users.
        :returns: dict
        """
        self.ensure_one()
        if not self.current_session_id:
            self._check_before_creating_new_session()
        self._validate_fields(self._fields)
        return self._action_to_open_mobile()

    def _action_to_open_mobile(self):
        _logger.info("_action_to_open_mobile")
        if not self.current_session_id:
            self.env['pos.session'].create({'user_id': self.env.uid, 'config_id': self.id})
        return self.current_session_id