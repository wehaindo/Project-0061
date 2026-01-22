odoo.define('weha_smart_pos_aeon_price.ProductItem', function (require) {
    "use strict";
    
    var ProductItem = require('point_of_sale.ProductItem');
    var models = require('point_of_sale.models');
    var Orderline = models.Orderline;
    const Registries = require('point_of_sale.Registries');


    var AeonPriceProductItem = ProductItem => class extends ProductItem {
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
    Registries.Component.extend(ProductItem, AeonPriceProductItem);

});