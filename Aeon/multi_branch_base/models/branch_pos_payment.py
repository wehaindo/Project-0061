from odoo import api, fields, models


class PosPayment(models.Model):
    _inherit = "pos.payment"

    operating_unit_ids = fields.Many2many(
        "operating.unit",
        "pos_payment_operating_unit_rel",
        string="Operating Units",
    )
    config_id = fields.Many2one(related="session_id.config_id", readonly=True)
    branch_id = fields.Many2one('res.branch', 'Store')


    @api.model
    def create(self, vals):
        pos_order_id = self.env["pos.order"].sudo().browse(vals.get("pos_order_id"))
        if pos_order_id.config_id:
            vals['branch_id'] = pos_order_id.config_id.res_branch_id.id
        return super(PosPayment, self).create(vals)