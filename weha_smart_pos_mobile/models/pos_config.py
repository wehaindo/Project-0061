from odoo import models, fields, api, _
import json


import logging
_logger = logging.getLogger(__name__)



class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.model
    def open_ui_mobile(self, uid, config_id):
        _logger.info("open_ui_mobile")
        pos_config_id = self.env['pos.config'].browse(config_id)
        _logger.info(pos_config_id.current_session_id)
        if not pos_config_id.current_session_id:
            _logger.info("create session")
            self.env['pos.session'].create({'user_id': uid, 'config_id': pos_config_id.id})
        return {"session_id": pos_config_id.current_session_id.id}