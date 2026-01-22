from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_floor_ids = fields.One2many(related='pos_config_id.floor_ids', readonly=False)
