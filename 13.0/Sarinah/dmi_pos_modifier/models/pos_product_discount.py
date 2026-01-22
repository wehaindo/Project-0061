from odoo import api, fields, models, tools
from string import ascii_letters, digits
from odoo.exceptions import ValidationError


class ProductDiscount(models.Model):
    _inherit = "srn.pos.product.discount"
    
    product_discount_line_ids = fields.One2many('srn.pos.product.discount.line', 'product_discount_id', string="Product Discount Line")

    @api.model
    def _cron_generate_pos_inventory_adjusment(self):
        srn_pos_product_discount = self.env['srn.pos.product.discount'].search([('start_date', '<=', fields.Date.today()), ('end_date', '>=', fields.Date.today()), ('active', '=', True)])
        srn_pos_product_discount.action_create_inventory_adjusment()

    def action_create_inventory_adjusment(self):
        # Dictionary to track product adjustments by location
        product_quantity_location = {}

        for rec in self:
            if rec.product_discount_line_ids:
                for line in rec.product_discount_line_ids:
                    product = line.product_id
                    if product:
                        # Grouping products by their location
                        location_id = line.location_id.id
                        if (product.id, location_id) not in product_quantity_location:
                            product_quantity_location[(product.id, location_id)] = {
                                'quantity': 0,
                                'location_id': location_id,
                                'branch_id': line.branch_id.id,
                            }

                        # Accumulate the quantities for the same product and location
                        product_quantity_location[(product.id, location_id)]['quantity'] += line.quantity

        inventory = self.env['stock.inventory']
        # Loop through the grouped data and create inventory adjustments for each unique (product, location)
        data_line = []
        location_ids = self.env['stock.location']
        product_ids = self.env['product.product']
        for (product_id, location_id), values in product_quantity_location.items():
            product = self.env['product.product'].browse(product_id)
            location = self.env['stock.location'].browse(location_id)

            data_line.append((0, 0, {
                'product_id': product_id,
                'product_qty': values['quantity'],
                'location_id': location_id
            }))

            location_ids |= location
            product_ids |= product
            branch_id = values['branch_id']


        if data_line:
            inventory = self.env['stock.inventory'].create({
                'name': f"INV: Pos Product Discount {fields.Date.today()}",
                'product_ids': [(6, 0, product_ids.ids)],
                'accounting_date': fields.Date.today(),
                'location_ids': [(6, 0, location_ids.ids)],
                'branch_id': branch_id,
                'line_ids': data_line,
            })

            difference_zero = all(line.difference_qty == 0 for line in inventory.line_ids)
            if difference_zero:
                inventory.sudo().unlink()
            else:
                inventory.write({'state': 'confirm'})
                inventory.action_validate()


class ProductDiscountLine(models.Model):
    _name = "srn.pos.product.discount.line"
    @api.depends('product_discount_id')
    def _compute_product_id(self):
        for res in self:
            product_discount_id = res.product_discount_id
            sku = product_discount_id.sku
            product = self.env['product.product'].search([('default_code', '=', sku)], limit=1)
            res.product_id = product.id

    product_discount_id = fields.Many2one('srn.pos.product.discount', string="Product Discount")
    product_id = fields.Many2one('product.product', string="Product", required=False, domain=[('type', '=', 'product')], compute = '_compute_product_id')
    quantity = fields.Float(string="Quantity", required=True)
    location_id = fields.Many2one('stock.location', string="Location", required=True, domain=[('usage', 'in', ['internal','transit'])])
    branch_id = fields.Many2one('res.branch', string="Branch", required=True)




    
