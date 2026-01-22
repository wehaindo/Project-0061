odoo.define('bi_pos_auto_discounts.discount', function(require) {
	"use strict";

	var { Order } = require('point_of_sale.models');
	const Registries = require('point_of_sale.Registries');

	const PosOrder = (Order) => class PosOrder extends Order {
		
		add_product(product, options){
			super.add_product(...arguments);
			var line = this.get_selected_orderline()
			var disc = product.product_discount;
			var member_disc = product.product_member_discount;
			// if (this.pos.config.allow_automatic_discount == true && disc != 0){
			// 	line.set_discount(disc)
			// }
			if(this.pos.config.allow_automatic_discount){
				var discount = disc + member_disc;				
				if (discount != 0){
					line.set_discount(discount);
				}
			}
		}
	}
	Registries.Model.extend(Order, PosOrder);
});
