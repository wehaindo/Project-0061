from odoo import _, fields, models, api
from odoo.modules.module import get_module_resource
import base64


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    shopon_pos_theme_primary_color = fields.Char(string="Header Color", readonly=False, default="#0e2954")
    setu_layout_view = fields.Selection(related='pos_config_id.setu_layout_view', readonly=False, required=1)
    

    def execute(self):
        res = super(ResConfigSettings, self).execute()
        file_path = "/shopon_pos_theme/static/src/scss/pos_variables_extra.scss"
        datas = base64.b64encode(("$primary:" + str(self.shopon_pos_theme_primary_color) + ";" or "\n").encode("utf-8"))
        custom_url = "/shopon_pos_theme/static/src/scss/pos_variables_extra.custom.point_of_sale.assets.scss"
        attachment = self.env["ir.attachment"].search([('name', '=', 'shopon_pos_variables_extra')])
        if attachment:
            attachment.unlink()
        ir_asset = self.env["ir.asset"].search([('name', '=', 'shopon_pos_variables_extra_override')])
        if ir_asset:
            ir_asset.unlink()
        new_attach = {
            'name': "shopon_pos_variables_extra",
            'type': "binary",
            'mimetype': ('text/scss'),
            'datas': datas,
            'url': custom_url,
        }
        self.env["ir.attachment"].create(new_attach)
        IrAsset = self.env['ir.asset']
        new_asset = {
            'path': custom_url,
            'target': file_path,
            'directive': 'replace',
        }
        new_asset['name'] = 'shopon_pos_variables_extra_override'
        new_asset['bundle'] = 'point_of_sale.assets'
        new_asset['sequence'] = self.env['ir.asset'].search([('path', 'like', custom_url)]).sequence or 16
        IrAsset.create(new_asset)
        self.env["ir.qweb"].clear_caches()
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        shopon_pos_theme_primary_color = self.env['ir.config_parameter'].sudo().get_param(
            'shopon_pos_theme.shopon_pos_theme_primary_color', "#0e2954")
        res.update(shopon_pos_theme_primary_color=shopon_pos_theme_primary_color)
        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].set_param('shopon_pos_theme.shopon_pos_theme_primary_color',
                                                  self.shopon_pos_theme_primary_color or "#0e2954")
        super(ResConfigSettings, self).set_values()
    
