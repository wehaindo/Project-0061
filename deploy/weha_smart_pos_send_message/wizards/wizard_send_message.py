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



class WizardSendMessage(models.TransientModel):
    _name = 'wizard.send.message'

    def send_message(self):
        config_id  = self._context.get('config_id', False)
        if config_id:
            # config_id = self.env['pos.config'].browse(config_id)
            notifications = []
            vals = {'config_id': config_id, 'message': self.message}
            notifications.append([self.env.user.partner_id,'pos.session/send_message', vals])
            if len(notifications) > 0:
                _logger.info('Notification')
                _logger.info(notifications)
                self.env['bus.bus']._sendmany(notifications)
            else:
                _logger.info('No Notification')
            return True
                        
                        
    message = fields.Char('Message', size=255, required=True)

    