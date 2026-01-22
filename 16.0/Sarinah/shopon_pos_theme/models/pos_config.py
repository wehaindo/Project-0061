from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'
   
    setu_layout_view = fields.Selection(
        [('grid_view', 'Grid View'), ('list_view', 'List View')], string='Layout View', default='grid_view', required=1)

