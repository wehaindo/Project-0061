odoo.define('weha_smart_pos_product_combo.ProductScreen', function(require) {
	"use strict";

	const Registries = require('point_of_sale.Registries');

	const ProductScreen = require('point_of_sale.ProductScreen'); 

	const ProductComboProductScreen = (ProductScreen) =>
		class extends ProductScreen {
			constructor() {
				super(...arguments);
			}

			async _clickProduct(event) {
				console.log('Product Clicked');
				var self = this;
				if (!this.currentOrder) {
					this.env.pos.add_new_order();
				}
				const product = event.detail;
				const options = await this._getAddProductOptions(product);
				// Do not add product if options is undefined.
				if (!options) return;
				
				console.log(product);
				let order = this.env.pos.get_order();
				if(product.to_weight && this.env.pos.config.iface_electronic_scale){
					this.gui.show_screen('scale',{product: product});
				}else{
					if(product.is_pack){
                        console.log('Product Pack Clicked');
						var required_products = [];
						var optional_products = [];
						var combo_products = self.env.pos.pos_product_pack;
						console.log(combo_products);
						if(product)
						{
							for (var i = 0; i < combo_products.length; i++) {
								console.log(combo_products[i]);
								if(combo_products[i]['bi_product_product'][0] == product['id'])
								{
									if(combo_products[i]['is_required'])
									{
										combo_products[i]['product_ids'].forEach(function (prod) {
											var sub_product = self.env.pos.db.get_product_by_id(prod);
											required_products.push(sub_product)
										});
									}
									else{
										combo_products[i]['product_ids'].forEach(function (prod) {
											var sub_product = self.env.pos.db.get_product_by_id(prod);
											optional_products.push(sub_product)
										});
									}
								}
							}
						}
						console.log(required_products);
						console.log(optional_products);
						self.showPopup('ProductComboSelectPopup', {'order':  this.env.pos.get_order(), 'product': product,'required_products':required_products,'optional_products':optional_products , 'update_line' : false });

					}
					else{
						console.log("Product Combo Add Product");
						//this.env.pos.get_order().add_product(product);
						await this._addProduct(product, options);
						// this.currentOrder.add_product(product,{});
					}
				}
			}

			_setValue(val){
				let self = this;
				let order = this.currentOrder;
				if(this.currentOrder.get_selected_orderline()){
					if(this.currentOrder.get_selected_orderline().product.is_pack){
						if(this.state.numpadMode==='quantity'){
							var orderline = order.get_selected_orderline()
	                    	orderline.set_quantity(val,'keep_price')

						}else{
							super._setValue(val)
						}
					}	
					else{
						super._setValue(val)
					}
				}
				
			}
		};

	Registries.Component.extend(ProductScreen, ProductComboProductScreen);

	return ProductScreen;

});
