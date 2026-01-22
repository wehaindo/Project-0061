odoo.define('weha_smart_pos_aeon_receipt.models', function(require){
    'use strict';
       
    var {  Order, Orderline } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
 
    const ReceiptOrderline = (Orderline) =>
    class extends Orderline {
        constructor(obj, options) {
            super(...arguments);
        }

        get_full_product_name () {
            var res = super.get_full_product_name();
            return "[" + this.product.default_code + "] " + res
        }
    }
 
    Registries.Model.extend(Orderline, ReceiptOrderline);
 
});