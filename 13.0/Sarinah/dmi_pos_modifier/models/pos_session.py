# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class PosSession(models.Model):
    _inherit = 'pos.session'

    def open_frontend_cb(self):
        """Open the pos interface with config_id as an extra argument.

        In vanilla PoS each user can only have one active session, therefore it was not needed to pass the config_id
        on opening a session. It is also possible to login to sessions created by other users.

        :returns: dict
        """
        if not self.ids:
            return {}

        product_promotion = self.env['srn.pos.product.discount']
        product_promotion._get_expired_promotions()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': '/pos/web?config_id=%d' % self.config_id.id,
        }

    def open_cashbox_pos(self):
        self.ensure_one()
        product_promotion = self.env['srn.pos.product.discount']
        product_promotion._get_expired_promotions()
        action = self.cash_register_id.open_cashbox_id()
        action['view_id'] = self.env.ref('point_of_sale.view_account_bnk_stmt_cashbox_footer').id
        action['context']['pos_session_id'] = self.id
        action['context']['default_pos_id'] = self.config_id.id
        return action

    def action_pos_session_open(self):
        # second browse because we need to refetch the data from the DB for cash_register_id
        # we only open sessions that haven't already been opened
        for session in self.filtered(lambda session: session.state in ('new_session', 'opening_control')):
            values = {}
            if not session.start_at:
                values['start_at'] = fields.Datetime.now()
            values['state'] = 'opened'
            session.write(values)
            session.statement_ids.button_open()
        product_promotion = self.env['srn.pos.product.discount']
        product_promotion._get_expired_promotions()
        return True

