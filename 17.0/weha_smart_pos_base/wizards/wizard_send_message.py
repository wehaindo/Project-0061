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
        active_id = self.env.context.get('active_id')
        pos_session_id = self.env['pos.session'].browse(active_id)
        if pos_session_id:
            # Send the live data to the frontend using the bus service
            channel = pos_session_id._get_bus_channel_name()
            message = {
                'channel': channel,
                'data': self.message
            }
            self.env["bus.bus"]._sendone(channel, "notification", message)
                        
    message = fields.Char('Message', size=255, required=True)

    