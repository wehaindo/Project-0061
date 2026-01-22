from odoo import api, fields, models


class PosSession(models.Model):
    _inherit = "pos.session"

    operating_unit_ids = fields.Many2many(
        "operating.unit",
        "pos_session_operating_unit_rel",
        string="Operating Units",
    )

    branch_id = fields.Many2one('res.branch', 'Store')

    @api.model
    def create(self, vals):
        config_id = self.env["pos.config"].sudo().browse(vals.get("config_id"))
        if config_id:
            vals['branch_id'] = config_id.res_branch_id.id
        return super(PosSession, self).create(vals)
