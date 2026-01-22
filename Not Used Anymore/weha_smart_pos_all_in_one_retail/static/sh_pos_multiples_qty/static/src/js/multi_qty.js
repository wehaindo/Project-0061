odoo.define('sh_pos_multiples_qty.multi_qty', function (require) {
    'use strict';

    var models = require("point_of_sale.models");
    var utils = require("web.utils");
    var round_pr = utils.round_precision;
    var field_utils = require('web.field_utils');
    const ProductScreen = require("point_of_sale.ProductScreen");
    const Registries = require("point_of_sale.Registries");


    models.load_fields("product.product", ["sh_multiples_of_qty"]);

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        set_quantity: function (quantity, keep_price) {
            this.order.assert_editable();
            if (quantity === 'remove') {
                this.order.remove_orderline(this);
                return;
            } else {
                var quant = typeof (quantity) === 'number' ? quantity : (field_utils.parse.float('' + quantity) || 0);
                var unit = this.get_unit();
                if (unit) {
                    if (unit.rounding) {
                        var decimals = this.pos.dp['Product Unit of Measure'];
                        var rounding = Math.max(unit.rounding, Math.pow(10, -decimals));
                        if (this.pos.config.sh_multi_qty_enable) {
                            var qty = parseInt(this.product.sh_multiples_of_qty)
                            if (qty) {
                                if (qty <= quant) {
                                    if (quant / qty == parseInt(quant / qty)) {
                                        var loop = quant / qty
                                    } else {
                                        var loop = quant / qty + 1
                                    }
                                    for (var i = 2; i <= loop; i++) {
                                        var val = qty * i
                                        quant = val
                                    }
                                }
                                else {
                                    quant = qty
                                }
                            }
                        }
                        this.quantity = round_pr(quant, rounding);
                        this.quantityStr = field_utils.format.float(this.quantity, { digits: [69, decimals] });
                    } else {
                        this.quantity = round_pr(quant, 1);
                        this.quantityStr = this.quantity.toFixed(0);
                    }
                } else {
                    this.quantity = quant;
                    this.quantityStr = '' + this.quantity;
                }
            }

            // just like in sale.order changing the quantity will recompute the unit price
            if (!keep_price && !this.price_manually_set) {
                this.set_unit_price(this.product.get_price(this.order.pricelist, this.get_quantity(), this.get_price_extra()));
                this.order.fix_tax_included_price(this);
            }
            
            var primary_uom = this.get_unit();
            if (this.pos.config.select_uom_type != 'secondary') {
                var secondary_uom = primary_uom;
                if (this.order.orderlines.models.includes(this)) {
                    this.is_secondary = true
                    secondary_uom = this.get_secondary_unit();
                }
            } else {
                this.is_secondary = true
                var secondary_uom = this.get_secondary_unit();
            }
            if (this.get_current_uom() == undefined) {
                this.set_current_uom(secondary_uom);
            }
            // // Initialization of qty when product added
            var current_uom = this.get_current_uom() || primary_uom;
            if (current_uom == primary_uom) {
                this.set_current_uom(primary_uom);
                this.set_primary_quantity(this.get_quantity());

                var converted_qty = this.convert_qty_uom(this.quantity, secondary_uom, current_uom);
                this.set_secondary_quantity(converted_qty);
                // just like in sale.order changing the quantity will recompute the unit price
                if (!keep_price && !this.price_manually_set) {
                    this.set_unit_price(this.product.get_price(this.order.pricelist, this.get_quantity()));
                    this.order.fix_tax_included_price(this);
                }
            } else {
                var converted_qty = this.convert_qty_uom(this.quantity, primary_uom, current_uom);
                this.set_primary_quantity(converted_qty);
                this.set_secondary_quantity(this.get_quantity());
                this.set_current_uom(secondary_uom);
                if (!keep_price && !this.price_manually_set) {
                    this.set_unit_price(this.product.get_price(this.order.pricelist, converted_qty));
                    this.order.fix_tax_included_price(this);
                }
            }
            
            this.trigger('change', this);
        },
    });

});
