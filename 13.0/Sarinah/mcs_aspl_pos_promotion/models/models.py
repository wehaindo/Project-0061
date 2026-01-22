# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta # add by yayat
import json

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        self.ensure_one()

        current_website = False

        if self.env.context.get('website_id'):
            current_website = self.env['website'].get_current_website()
            if not pricelist:
                pricelist = current_website.get_current_pricelist()

        combination_info = super(ProductTemplate, self)._get_combination_info(
            combination=combination, product_id=product_id, add_qty=add_qty, pricelist=pricelist,
            parent_combination=parent_combination, only_template=only_template)

        if self.env.context.get('website_id'):
            product = self.env['product.product'].sudo().browse(combination_info['product_id'])
            if not product:
                product = self.env['product.product'].sudo().search([('product_tmpl_id','=',self.id)])
                print('keluar ga',product)
            partner = self.env.user.partner_id
            company_id = current_website.company_id
            tax_display = self.env.user.has_group(
                'account.group_show_line_subtotals_tax_excluded') and 'total_excluded' or 'total_included'
            Fpos_sudo = self.env['account.fiscal.position'].sudo()
            fpos_id = Fpos_sudo.with_context(force_company=company_id.id).get_fiscal_position(partner.id)
            taxes = Fpos_sudo.browse(fpos_id).map_tax(
                product.sudo().taxes_id.filtered(lambda x: x.company_id == company_id), product, partner)
            quantity_1 = 1

            price_discount = 0
            print("MASSSSSSS", product)
            for prd in product:
                default_pricelist = self.env['ir.config_parameter'].sudo().get_param('default_price_list_thamrin')
                domain_price = [('pricelist_id', '=', int(default_pricelist)), ('product_id', '=', prd.id)]

                pricelistt = self.env['product.pricelist.item'].sudo().search(domain_price, order="id desc", limit=1)
                # if combination_info['product_id']:
                # price = taxes.compute_all(pricelistt.fixed_price, pricelist.currency_id, quantity_1, product, partner)[
                #     tax_display]

                combination_info['list_price'] = self.env['account.tax']._fix_tax_included_price_company(
                    pricelistt.fixed_price, product.sudo().taxes_id, taxes, company_id)
                list_price = taxes.compute_all(pricelistt.fixed_price, pricelist.currency_id, quantity_1, product,
                                  partner)[tax_display]
                price_discount = (pricelistt.fixed_price - (
                        pricelistt.fixed_price * (product.discount_id.discount_percentage / 100)))
                # price = price_discount
                print(prd, "PRD")

                if prd.discount_id:

                    is_discount = True
                    combination_info['price'] = self.env['account.tax']._fix_tax_included_price_company(
                        price_discount, product.sudo().taxes_id, taxes, company_id)
                    price = taxes.compute_all(price_discount, pricelist.currency_id, quantity_1, product, partner)[
                        tax_display]

                    print(price, 'price_disc')
                    print(combination_info['price'], 'price_disc 2')
                    print('masuk sini')
                    combination_info.update({
                        'has_discounted_price': is_discount,
                        'price': price,
                        'price_discount': price_discount,
                        'list_price': pricelistt.fixed_price
                    })

                    # return {
                    #     'price': price_discount,
                    # }
                    combination_info.update(
                        list_price=list_price,
                        price=price,
                        has_discounted_price=True,
                    )
            print("MASUK SINI 3")
            print(combination_info)

        return combination_info

class InheritPosPromotion(models.Model):
    _inherit = 'pos.promotion'

    def cron_deactivate_promotion(self, days):
        pass
    
    sequence_number = fields.Char(string='Sequence #', readonly=True, required=True, copy=False, default='New')
    # add by yayat
    remark = fields.Text(string="Remark", readonly=True)

    @api.model
    def get_buy_x_get_y(self, order):
        print(order)
        list_bxgyf = []
        list_promotion_line_id = []

        for line in order['lines']:
            if line[2]['free_product_y_id'] or line[2]['free_product_x_id']:
                promotion_line_id = line[2]['free_product_x_id'] or line[2]['free_product_y_id']
                if promotion_line_id not in list_promotion_line_id:
                    list_promotion_line_id.append(promotion_line_id)
                list_bxgyf.append({
                    'product_id': line[2]['product_id'],
                    'qty': line[2]['qty'],
                    'price_unit': line[2]['price_unit'],
                    'price_subtotal_incl': line[2]['price_subtotal_incl'],
                    'promotion_line_id': promotion_line_id,
                    'is_x_product': True if line[2]['free_product_x_id'] else False,
                    'is_y_product': True if line[2]['free_product_y_id'] else False,
                })

        # print(list_promotion_line_id)
        # print(list_bxgyf)
        list_final = []
        list_promotion_line_id_final = []
        for line_id in list_promotion_line_id:
            promotion_line = self.env['pos.conditions'].search([('id', '=', line_id)])
            qty_promotion = promotion_line.quantity
            qty_free = promotion_line.quantity_y
            if promotion_line.operator == 'is_eql_to':
                is_multiply = False
            else:
                is_multiply = True

            qty = 0
            list_x = list(filter(lambda x: x['is_x_product'] and x['promotion_line_id'] == line_id, list_bxgyf))
            for lx in list_x:
                qty += lx['qty']

            if is_multiply:
                qty_div = int(qty / qty_promotion)
                if qty_div != 0:
                    qty_free *= qty_div
                    qty_promotion *= qty_div

            if qty >= qty_promotion:

                list_y = list(filter(lambda x: x['is_y_product'] and x['promotion_line_id'] == line_id, list_bxgyf))
                if list_y:
                    list_promotion_line_id_final.append(line_id)
                    list_y_min = min(list_y, key=lambda i: (i['price_unit']))

                    is_new_line = False
                    new_qty = list_y_min['qty']
                    if qty == qty_promotion:
                        is_new_line = True
                    else:
                        qty_exc = qty - new_qty
                        if qty_exc < qty_promotion:
                            selisih = qty - qty_promotion
                            if selisih > qty_free:
                                selisih -= qty_free
                            new_qty -= selisih
                            is_new_line = True
                        else:
                            if new_qty > qty_free:
                                new_qty -= qty_free
                                is_new_line = True
                            else:
                                new_qty = qty_free

                    free_product_x_id = None
                    if list_y_min['product_id'] in [x.id for x in promotion_line.product_x_id]:
                        free_product_x_id = promotion_line.id

                    list_final.append({
                        'promotional_id': promotion_line.pos_promotion_rel.id,
                        'vendor_id': promotion_line.pos_promotion_rel.vendor_id.id,
                        'vendor_shared': promotion_line.pos_promotion_rel.vendor_shared,
                        'sarinah_shared': promotion_line.pos_promotion_rel.sarinah_shared,
                        'promotion_code': promotion_line.pos_promotion_rel.promotion_code,
                        'product_id': list_y_min['product_id'],
                        'is_new_line': is_new_line,
                        'new_qty': new_qty,
                        'free_qty': qty_free,
                        'free_product_y_id': promotion_line.id,
                        'free_product_x_id': free_product_x_id,
                    })
        data = {
            'promotion_line_id': list_promotion_line_id_final,
            'list_final': list_final,
        }
        Json = json.dumps(data)
        print(Json)
        return Json

    # Sequence Number Method
    @api.model
    def create(self, vals):
        vals['sequence_number'] = self.env['ir.sequence'].next_by_code('pos.promotional.discount') or _('New')
        return super(InheritPosPromotion, self).create(vals)

    vendor_id = fields.Many2one(comodel_name='res.partner', string='Vendor Name',
                                ondelete='set null', index=True, contex={}, domain=[])
    vendor_shared = fields.Float(string='Vendor Shared (%)', digits=(5, 2))
    sarinah_shared = fields.Float(string='Sarinah Shared (%)', digits=(5, 2), readonly=True)

    product_id_qty = fields.Many2many('product.product','pos_product_id_qty_rel', string='Products')

    available_in_pos = fields.Many2many('pos.config', string="POS Config")
    promotion_type = fields.Selection(selection_add=[('discount_on_product', 'Discount on Product (Seasonal & On Top)'),
                                                     ('discount_on_customer', 'Discount Based on Customer')])
    discount_on_products = fields.Many2many('product.product', 'pos_discount_on_products_rel', string='Products')
    discount = fields.Float('Discount(%)')

    type_disc_qty = fields.Selection(selection=[('multiply', 'Multiply'),
                                                 ('equal', 'Equal'), ], default='multiply',
                                     string='Discount Quantity Type')

    discount_seasonal_ids = fields.One2many('discount.seasonal','pos_promotion_id', copy=True)

    state = fields.Selection(string="State ", default="draft",
                             selection=[("draft", "Draft "),
                                        ("approve1", "Waiting for Approval 1"),
                                        ("approve2", "Waiting for Approval 2"),
                                        ("approved", "Approved")], )

    total_discount_vip = fields.Float('Total Discount For VIP (%)')

    total_discount_emp = fields.Float('Total Discount For Employee (%)')

    percent_discount_reg = fields.Float('Total Discount For Reguler (%)')
    percent_discount_emp = fields.Float('Total Discount For Employee (%)')
    percent_discount_vip = fields.Float('Total Discount For VIP (%)')

    # one2many

    pos_condition_ids = fields.One2many('pos.conditions', 'pos_promotion_rel', copy=True)
    pos_quntity_ids = fields.One2many('quantity.discount', 'pos_quantity_rel', copy=True)
    pos_quntity_amt_ids = fields.One2many('quantity.discount.amt', 'pos_quantity_amt_rel', copy=True)
    pos_quntity_dis_ids = fields.One2many('get.discount', 'pos_quantity_dis_rel', copy=True)
    multi_products_discount_ids = fields.One2many('discount.multi.products','multi_product_dis_rel', copy=True)
    multi_categ_discount_ids = fields.One2many('discount.multi.categories','multi_categ_dis_rel', copy=True)
    discount_price_ids = fields.One2many('discount.above.price','pos_promotion_id', copy=True)

    @api.onchange('vendor_shared')
    def _onchange_discount_shared(self):
        self.sarinah_shared = 100 - self.vendor_shared
        if self.sarinah_shared < 0:
            self.sarinah_shared = 0

    @api.onchange('vendor_id')
    def _onchange_vendor_id(self):
        self.pos_condition_ids = None
        self.pos_quntity_ids = None
        self.product_id_qty = None
        self.product_id_amt = None
        self.multi_products_discount_ids = None
        self.multi_categ_discount_ids = None
        self.discount_seasonal_ids = None

    def action_confirm(self):
        self.state = 'approve1'

    def action_approve1(self):
        self.state = 'approve2'
        # Add By yayat
        remark = ""
        if self.remark:
            remark = f"{self.remark}Approve 1 By {self.env.user.name} at {(datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')}\n"
        else:
            remark = f"Approve 1 By {self.env.user.name} at {(datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')}\n"

        self.write({"remark": remark})

    def action_approve2(self):
        self.state = 'approved'
        # Add By yayat
        remark = ""
        if self.remark:
            remark = f"{self.remark}Approve 2 By {self.env.user.name} at {(datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')}\n"
        else:
            remark = f"Approve 2 By {self.env.user.name} at {(datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')}\n"

        self.write({"remark": remark})

    def action_set_to_draft(self):
        self.state = 'draft'

    ## Add By Yayat ##
    @api.onchange("promotion_type")
    def _promotion_type_onchange(self):
        if self.promotion_type == "dicount_total":
            self.vendor_id = None


class PosDiscountSeasonal(models.Model):
    _name = 'discount.seasonal'

    pos_promotion_id = fields.Many2one(comodel_name='pos.promotion', string="Promotion")
    active = fields.Boolean(related="pos_promotion_id.active")
    discount_type = fields.Selection(string="Discount Type", default="seasonal",
                             selection=[("seasonal", "Seasonal "),
                                        ("on_top", "On Top"),
                                        ], )
    products_discount_1 = fields.Float("Discount 1")
    products_discount_2 = fields.Float("Discount 2")
    products_discount = fields.Float("Discount")
    product_ids = fields.Many2many(comodel_name='product.product', string="Products")

    @api.onchange('discount_type', 'products_discount_1', 'products_discount_2')
    def onchange_discount_type(self):
        self.products_discount = 0
        if self.discount_type == 'on_top':
            self.products_discount = (1 - ((1 - (self.products_discount_1 / 100)) * (1 - (self.products_discount_2 / 100)))) * 100


class PosConfig(models.Model):
    _inherit = 'pos.config'

    promotion_ids = fields.Many2many('pos.promotion', string="Promotions")


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    custom_promotion_id = fields.Many2one(comodel_name='pos.promotion', string="Custom Promotion")

    vendor_id = fields.Many2one(comodel_name='res.partner', string='Vendor Name',
                                ondelete='set null', index=True, contex={}, domain=[])
    vendor_shared = fields.Float(string='Vendor Shared (%)', digits=(5, 2))
    sarinah_shared = fields.Float(string='Sarinah Shared (%)', digits=(5, 2))
    fix_discount = fields.Float(string='Fix Amount Discount')


class InheritPosPromotionCateg(models.Model):
    _inherit = 'discount.multi.categories'

    categ_ids = fields.Many2many(comodel_name='product.category', string="Categories")


class GetProductDiscount(models.Model):
    _inherit = 'get.discount'

    product_id_dis = fields.Many2many(comodel_name='product.product', string='Product')


class InheritConditionsData(models.Model):
    _inherit = 'pos.conditions'

    product_x_id = fields.Many2many('product.product', 'pos_conditions_product_x_rel', string='Product(X)')
    product_y_id = fields.Many2many('product.product', 'pos_conditions_product_product_y_rel', string='Product(Y)')


# class PosOrderLine(models.Model):
#     _inherit = 'pos.order.line'
#
#     custom_discount_id = fields.Many2one(comodel_name='pos.custom.discount', string="Custom Discount")

