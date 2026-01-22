from datetime import datetime
from uuid import uuid4
import pytz
import string
import random

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError


import logging
_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    def open_fast_login(self):
        self.ensure_one()
        domain = [
            ('state','in',['opening_control','opened','closing_control']),
            ('user_id','=', self.env.uid),
            ('config_id','=', self.id)
        ]
        pos_session_id = self.env['pos.session'].search(domain, limit=1)
        if not pos_session_id:
            self._check_before_creating_new_session()
        self._validate_fields(self._fields)    
        return self._action_to_open_ui()


    def _action_to_open_ui(self):
        domain = [
            ('state','in',['opening_control','opened','closing_control']),
            ('user_id','=', self.env.uid),
            ('config_id','=', self.id)
        ]
        pos_session_id = self.env['pos.session'].search(domain, limit=1)
        if not pos_session_id:
            _logger.info("Session not found then create new session")
            self.env['pos.session'].create({'user_id': self.env.uid, 'config_id': self.id})
        else:
            _logger.info("Session found then continue with current session")


    def generate_code(self):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))  
        self.pos_config_code = code

    pos_config_code = fields.Char('Code #', size=20)


    @api.model
    def create(self, vals):
        res = super(PosConfig, self).create(vals)
        res.generate_code()
        return res

    def write(self, vals):
        super(PosConfig, self).write(vals)
        if not self.pos_config_code:
            self.generate_code()
            