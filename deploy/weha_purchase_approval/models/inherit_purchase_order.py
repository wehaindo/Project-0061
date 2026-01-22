from odoo import fields, models
# from odoo.exceptions import UserError, ValidationError


class InheritPurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_send_approval(self):
        # mail_t = False


        # rule = self.env['weha.purchase.approval.rule'].search(args)
        # for line in rule:
        #     mail_t = line.mail_tamplate_id


        # args = [('id', '=', mail_t.id)]
        # template_ids = self.env['mail.template'].search(args)  # search tamplate dengan nama : Request for Cancel
        # template_ids.sudo().send_mail(self.id, force_send=True)

        self.state = 'waiting_approval_manager'

    def action_approval_manager(self):
        self.state = 'waiting_approval_senior'

    def action_approval_senior(self):
        self.state = 'sent'

    def action_reject(self):
        self.state = 'reject'

    state = fields.Selection(selection_add=[('waiting_approval_manager','Waiting Approval Manager'), ('waiting_approval_senior','Waiting Approval Senior'), ('reject','Reject')])
    
    
    
    
