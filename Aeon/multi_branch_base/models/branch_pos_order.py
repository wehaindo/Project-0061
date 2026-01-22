from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    operating_unit_ids = fields.Many2many(
        "operating.unit",
        "pos_order_operating_unit_rel",
        string="Operating Units",
    )

    branch_id = fields.Many2one("res.branch","Store")
    config_id = fields.Many2one(related="session_id.config_id", readonly=True)

    @api.model
    def create(self, vals):
        session_id = self.env["pos.session"].sudo().browse(vals.get("session_id"))
        if session_id.config_id:
            vals['branch_id'] = session_id.config_id.res_branch_id.id
        return super(PosOrder, self).create(vals)


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    operating_unit_ids = fields.Many2many(
        "operating.unit",
        "pos_order_line_operating_unit_rel",
        string="Operating Units",
    )

    branch_id = fields.Many2one("res.branch","Store")

    @api.model
    def create(self, vals):
        order_id = self.env["pos.order"].sudo().browse(vals.get("order_id"))
        if order_id.config_id:
            vals['branch_id'] = order_id.config_id.res_branch_id.id
        return super(PosOrderLine, self).create(vals)