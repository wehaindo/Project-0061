from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


import logging
_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def action_receipt_to_customer(self, name, client, ticket):
        if not self:
            return False
        if not client.get('email'):
            return False
        
        template = self.env.ref('weha_smart_pos_aeon_email_receipt.pos_email_receipt_template')
        if not template:
            return False
        
        filename = 'Receipt-' + name + '.jpg'
        receipt = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': ticket,
            'res_model': 'pos.order',
            'res_id': self.ids[0],
            'mimetype': 'image/jpeg',
        })
        attachment = [(6,0, [receipt.id])]                                     
        
        # Attach the file and send the email
        template.write({
            'email_to': client.get('email'),
            'attachment_ids': attachment
        })
        mail_id = template.send_mail(self.ids[0], force_send=True)
        return mail_id
                       