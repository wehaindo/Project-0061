from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError


class WizardPosRfid(models.TransientModel):
    _name = 'wizard.pos.rfid'
    _description = 'Setup Cashier RFID'

    rfid = fields.Char('RFID', size=100)

    def set_rfid(self):
        res_users_id = self.env["res.users"].browse(self.env.context['active_id'])
        res_users_id._change_password(self.rfid)
        res_users_id.rfid = self.rfid

    