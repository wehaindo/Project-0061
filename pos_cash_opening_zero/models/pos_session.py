from odoo import models

class PosSession(models.Model):
    _inherit = 'pos.session'

    def open_session_cb(self):
        # Call the super method to handle the usual logic
        super(PosSession, self).open_session_cb()
        
        # Ensure the opening balance is set to 0
        for session in self:
            session.cash_register_balance_start = 0.0
