from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    res_branch_id = fields.Many2one("res.branch",string="Store")