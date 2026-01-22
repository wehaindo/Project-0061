from datetime import datetime
from uuid import uuid4
import pytz
import string
import random

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError


class PosConfig(models.Model):
    _inherit = 'pos.config'


    def open_fast_login(self):
        self.ensure_one()
        if not self.current_session_id:
            self._check_before_creating_new_session()
        self._validate_fields(self._fields)

        # check if there's any product for this PoS
        domain = [('available_in_pos', '=', True)]
        if self.limit_categories and self.iface_available_categ_ids:
            domain.append(('pos_categ_id', 'in', self.iface_available_categ_ids.ids))
        if not self.env['product.product'].search(domain):
            return {
                'name': _("There is no product linked to your PoS"),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'pos.session.check_product_wizard',
                'target': 'new',
                'context': {'config_id': self.id}
            }

        return self._action_to_open_ui()


    def _action_to_open_ui(self):
        if not self.current_session_id:
            self.env['pos.session'].create({'user_id': self.env.uid, 'config_id': self.id})
        # path = '/pos/web' if self._force_http() else '/pos/ui'
        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': path + '?config_id=%d' % self.id,
        #     'target': 'self',
        # }


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
            