from odoo import _, fields, models, api
from odoo.modules.module import get_module_resource
import base64


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    shopon_pos_theme_primary_color = fields.Char(string="Header Color", readonly=False, default="#0e2954")
    setu_display_stock = fields.Boolean(related='pos_config_id.setu_display_stock', readonly=False)
    setu_stock_type = fields.Selection(related='pos_config_id.setu_stock_type', readonly=False)
    setu_continous_sale = fields.Boolean(related='pos_config_id.setu_continous_sale', readonly=False)
    setu_deny_val = fields.Integer(related='pos_config_id.setu_deny_val', readonly=False)
    setu_error_msg = fields.Char(related='pos_config_id.setu_error_msg', readonly=False)
    setu_hide_out_of_stock = fields.Boolean(related='pos_config_id.setu_hide_out_of_stock', readonly=False)
    setu_layout_view = fields.Selection(related='pos_config_id.setu_layout_view', readonly=False, required=1)
    setu_receipt_design = fields.Many2one(related='pos_config_id.setu_receipt_design', string="Receipt Design",
                                          help="Choose any receipt design", compute='_compute_pos_is_custom_receipt',
                                          readonly=False, store=True)
    setu_design_receipt = fields.Text(related='pos_config_id.setu_design_receipt', string='Receipt XML')
    is_custom_receipt = fields.Boolean(related='pos_config_id.is_custom_receipt', readonly=False, store=True)

    setu_pos_enable_product_variants = fields.Boolean(related='pos_config_id.setu_pos_enable_product_variants',
                                                      string='Enable Product Variants', readonly=False, store=True)
    setu_close_popup_after_single_selection = fields.Boolean(
        related='pos_config_id.setu_close_popup_after_single_selection',
        string='Auto close popup after single variant selection', readonly=False, store=True)
    setu_pos_display_alternative_products = fields.Boolean(
        related='pos_config_id.setu_pos_display_alternative_products', string='Display Alternative product',
        readonly=False, store=True)
    setu_pos_variants_group_by_attribute = fields.Boolean(related='pos_config_id.setu_pos_variants_group_by_attribute',
                                                          string='Group By Attribute', readonly=False, store=True)

    setu_is_hide_financial_details = fields.Boolean(related='pos_config_id.setu_is_hide_financial_details',
                                                    readonly=False, store=True)

    @api.depends('pos_is_custom_receipt', 'pos_config_id')
    def _compute_pos_is_custom_receipt(self):
        for res_config in self:
            if res_config.pos_is_custom_receipt:
                res_config.pos_receipt_design = res_config.pos_config_id.receipt_design
            else:
                res_config.pos_receipt_design = False

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

    @api.model
    def setu_pos_fetch_pos_stock(self, kwargs):
        result = {}
        setu_stock_type = kwargs['setu_stock_type']
        setu_hide_out_of_stock = kwargs['setu_hide_out_of_stock']
        config_id = self.env['pos.config'].browse([kwargs.get('config_id')])
        picking_type = config_id.picking_type_id
        location_id = picking_type.default_location_src_id.id
        product_obj = self.env['product.product']
        pos_products = product_obj.search([('sale_ok', '=', True), ('available_in_pos', '=', True)])
        pos_products_qtys = pos_products.with_context(location=location_id)._compute_quantities_dict(lot_id=None,
                                                                                                     owner_id=None,
                                                                                                     package_id=None)
        for pos_product in pos_products_qtys:
            if setu_stock_type == 'available_qty':
                if setu_hide_out_of_stock and pos_products_qtys[pos_product]['qty_available'] > 0:
                    result[pos_product] = pos_products_qtys[
                        pos_product]['qty_available']
                if not setu_hide_out_of_stock:
                    result[pos_product] = pos_products_qtys[
                        pos_product]['qty_available']
            elif setu_stock_type == 'forecasted_qty':
                if setu_hide_out_of_stock and pos_products_qtys[pos_product]['virtual_available'] > 0:
                    result[pos_product] = pos_products_qtys[
                        pos_product]['virtual_available']
                if not setu_hide_out_of_stock:
                    result[pos_product] = pos_products_qtys[
                        pos_product]['virtual_available']
            else:
                if setu_hide_out_of_stock and pos_products_qtys[pos_product]['qty_available'] - \
                        pos_products_qtys[pos_product]['outgoing_qty'] > 0:
                    result[pos_product] = pos_products_qtys[pos_product][
                                              'qty_available'] - pos_products_qtys[pos_product]['outgoing_qty']
                if not setu_hide_out_of_stock:
                    result[pos_product] = pos_products_qtys[pos_product][
                                              'qty_available'] - pos_products_qtys[pos_product]['outgoing_qty']
        return result
