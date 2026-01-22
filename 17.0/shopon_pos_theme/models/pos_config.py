from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    setu_display_stock = fields.Boolean('Display stock in POS', default=True)
    setu_stock_type = fields.Selection(
        [('available_qty', 'Available Quantity(On hand)'), ('forecasted_qty', 'Forecasted Quantity'),
         ('virtual_qty', 'Quantity on Hand - Outgoing Qty')], string='Stock Type', default='available_qty')
    setu_continous_sale = fields.Boolean('Allow Order When Out-of-Stock')
    setu_deny_val = fields.Integer('Deny order when product stock is lower than ')
    setu_error_msg = fields.Char(string='Custom message', default="Product out of stock")
    setu_hide_out_of_stock = fields.Boolean(string="Hide Out of Stock products", default=False)
    setu_layout_view = fields.Selection(
        [('grid_view', 'Grid View'), ('list_view', 'List View')], string='Layout View', default='grid_view', required=1)

    setu_receipt_design = fields.Many2one('pos.receipt', string="Receipt Design", help="Choose any receipt design")
    setu_design_receipt = fields.Text(related='setu_receipt_design.setu_design_receipt', string='Receipt XML')
    is_custom_receipt = fields.Boolean(string='Is Custom Receipt')
    setu_pos_enable_product_variants = fields.Boolean(
        string='Enable Product Variants')
    setu_close_popup_after_single_selection = fields.Boolean(
        string='Auto close popup after single variant selection')
    setu_pos_display_alternative_products = fields.Boolean(string='Display Alternative product')
    setu_pos_variants_group_by_attribute = fields.Boolean(string='Group By Attribute', default=False)
    setu_is_hide_financial_details = fields.Boolean(string='Hide financial details [Margin And Cost]', default= True)