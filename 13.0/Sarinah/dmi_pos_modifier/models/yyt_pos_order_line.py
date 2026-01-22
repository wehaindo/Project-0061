from odoo import api, fields, models, tools


class YytPosOrderLine(models.Model):
    _inherit = "yyt.pos.order.line"
    
    location_brand = fields.Char(string="Location Brand")
    lantai = fields.Char(string="Lantai")
    luas = fields.Char(string="Luas")
    custom_promotion_id = fields.Many2one('pos.promotion', string='Promotion')
    
    def init(self):
        cr = self.env.cr
        tools.drop_view_if_exists(cr, "yyt_pos_order_line")
        cr.execute(
            """
        CREATE OR REPLACE VIEW yyt_pos_order_line AS
        (
            select
            pol.id,
            po.name as order_ref,
            po.date_order,
            po.pos_reference as receipt_number,
            product.sku,
            product.product_name,
            product.owner_name,
            product.categ_name,
            product.brand_name,
            product.is_consignment,
            pol.price_unit as sales_price,
            pol.qty as qty,
            pol.sh_exchange_qty as exchange_qty,
            pol. sh_return_qty as return_qty,
            pol.discount as discount_perc,
            pol.fix_discount as discount_fix,
            pol.price_subtotal as total_wo_tax,
            pol.price_subtotal_incl as total_w_tax,
            pol.consignment_margin::text as sarinah_margin,
            (100 - pol.consignment_margin::int)::text as vendor_margin,
            COALESCE(pol.custom_fix_promotion_id, pol.custom_promotion_id) AS custom_promotion_id,
            pol.vendor_shared::text as vendor_discount_shared,
            pol.sarinah_shared::text as sarinah_discount_shared,
            pc.name as pos_name,
            cs.name as customer,
            po.cashier,
            dept.name as department_name,
            rb.name as branch_name,
            loc.complete_name as location_name,
            -- po.loyalty_points AS earn_points, po.loyalty_burn_points AS burn_points,
            ref_sa.name as referral_sa,
            ref_code.name as referral_code,
            product.luas,
            product.lantai,
            product.location_brand,
            po.is_return_order,
            po.is_exchange_order
        from
            pos_order_line pol
        left join pos_order po on
            po.id = pol.order_id
        left join (
            select
                pp.id,
                pp.default_code as sku,
                pt.name as product_name,
                rp.name as owner_name,
                pc.complete_name as categ_name,
                pb.name as brand_name,
                pt.is_consignment,
                pb.lantai as lantai,
                pb.luas as luas,
                loc.complete_name as location_brand
            from
                product_product pp
            left join product_template pt on
                pt.id = pp.product_tmpl_id
            left join res_partner rp on
                rp.id = pt.owner_id
            left join product_category pc on
                pc.id = pt.categ_id
            left join product_brand pb on
                pb.id = pt.brand_id
            left join stock_location loc on
                loc.id = pb.location_id
                    ) product on product.id = pol.product_id
        left join res_partner cs on
            cs.id = po.partner_id
        left join hr_department dept on
            dept.id = po.department_id
        left join res_branch rb on
            rb.id = po.branch_id
        left join stock_location loc on
            loc.id = po.location_id
        left join pos_config pc on
            pc.id = po.config_id
        left join pos_referral_code ref_sa on
            ref_sa.id = pos_ref_code_id
        left join pos_referral_code2 ref_code on
            ref_code.id = pos_ref_code2_id
        order by
            po.date_order desc
        )
        """
        )