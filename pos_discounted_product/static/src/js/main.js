/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_disounted_product.main', function (require) {
    "use strict";
    
    var ProductItem = require('point_of_sale.ProductItem');
    var models = require('point_of_sale.models');
    var Orderline = models.Orderline;
    const Registries = require('point_of_sale.Registries');


    const WkOrderline = (Orderline) => class extends Orderline {
        constructor(obj, options) {
            super(...arguments);
            var self = this;
            self.original_prices = options.original_prices || false
            if (options.json) {
                var wk_json = options.json
                if (wk_json.original_price)
                    self.original_prices = wk_json.original_prices
            }
        }
        export_for_printing() {
            var self=this
            var dict = super.export_for_printing(...arguments);
            dict.original_prices = self.product.lst_price * dict.quantity
            return dict;
        }
    }
    Registries.Model.extend(Orderline, WkOrderline);

    var PosResProductItem = ProductItem => class extends ProductItem {
        get original_price() {
            const formattedUnitPrice = this.env.pos.format_currency(this.props.product.lst_price, 'Product Price');
            if (this.props.product.to_weight) {
                return `${formattedUnitPrice}/${this.env.pos.units_by_id[this.props.product.uom_id[0]].name}`;
            }
            else {
                return formattedUnitPrice;
            }
        }
        get original_price_unit() {
            return this.props.product.lst_price
        }
        get price_unit() {
            return this.props.product.get_price(this.pricelist, 1)
        }
    }
    Registries.Component.extend(ProductItem, PosResProductItem);

    Registries.Component.freeze();
    

});
