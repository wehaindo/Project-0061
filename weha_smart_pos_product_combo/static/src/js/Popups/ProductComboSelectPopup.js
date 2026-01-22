odoo.define('weha_smart_pos_product_combo.ProductComboSelectPopup', function(require){
	'use strict';

	const Popup = require('point_of_sale.ConfirmPopup');
	const Registries = require('point_of_sale.Registries');
	const { onMounted, useRef, useState } = owl;


	class ProductComboSelectPopup extends Popup {

		constructor() {
			super(...arguments);
			// this.state = useState(
            //     { 
			// 		order: this.props.order,
			// 		product: this.props.product,
			// 		update_line: this.props.update_line,
			// 		required_products: this.props.required_products,
			// 		optional_products: this.props.optional_products,
			// 		combo_products: this.props.pos_product_pack
            //     }
            // );
			// onMounted(this._mounted);
		}

		go_back_screen() {
			this.showScreen('ProductScreen');
			this.trigger('close-popup');
		}

		get req_product() {
			let req_product = [];
			$.each(this.props.required_products, function( i, prd ){
				prd['product_image_url'] = `/web/image?model=product.product&field=image_128&id=${prd.id}&write_date=${prd.write_date}&unique=1`;
				req_product.push(prd)
			});
			return req_product;
		}

		get optional_product(){
			let optional_product = [];
			$.each(this.props.optional_products, function( i, prd ){
				prd['product_image_url'] = `/web/image?model=product.product&field=image_128&id=${prd.id}&write_date=${prd.write_date}&unique=1`;
				optional_product.push(prd)
			});
			return optional_product;
		}

		_mounted(){
			var self = this;
			var order = this.pos.get_order();
			console.log(order);
			if(order){
				var orderlines = order.get_orderlines();
				this.product = self.props.product;
				this.update_line = self.props.update_line;
				this.required_products = self.props.required_products;
				this.optional_products = self.props.optional_products;
				this.combo_products = self.env.pos.pos_product_pack;
				
				// $('.optional-product').each(function(){
				// 	if(self.update_line){
				// 		$(this).on('click',function () {
	            //             if($(this).hasClass('raghav')){
	            //             	$(this).removeClass('raghav');
	            //             }else{
	            //             	$(this).addClass('raghav');
	            //             }
				// 		});
	            //         var selectedprod = parseInt(this.dataset.productId);
	            //         var order = self.env.pos.get_order();
	            //         var selected_product = order.get_selected_orderline()
	            //         if(order){
	            //             if (order.get_selected_orderline()) {
	            //                 if(order.get_selected_orderline().product.id == self.product.id){
	            //                     var selected_product = order.get_selected_orderline().combo_prod_ids
	            //                     var combo_products = self.env.pos.pos_product_pack;
	            //                     for (var i = 0; i < selected_product.length; i++){
	            //                         if(selected_product[i] == selectedprod){
	            //                             $(this).addClass('raghav');
	            //                         }
	            //                     };
	            //                 }
	            //             }
	            //         }
	            //     }
	            //     else{
	            //     	$(this).on('click',function () {
	            //             if( $(this).hasClass('raghav') ){
	            //             	$(this).removeClass('raghav');
	            //             }else{
	            //             	$(this).addClass('raghav');
	            //             }
				// 		});
	            //     }
				// });
			}

		}
		
		renderElement() {
			var self = this;
			var order = self.env.pos.get_order();
			if(order){
				var orderlines = order.get_orderlines();
				var final_products = this.required_products;
				$('.remove-product').click(function(ev){
					ev.stopPropagation();
					ev.preventDefault();
					var prod_id = parseInt(this.dataset.productId);
					$(this).closest(".optional-product").hide();
					for (var i = 0; i < self.optional_products.length; i++)
					{
						if(self.optional_products[i]['id'] == prod_id)
						{
							self.optional_products.splice(i, 1);
						}
					}
				});
			}
		}

		add_confirm(ev){
			var final_products = this.required_products;
			var order = this.env.pos.get_order();
			var orderlines = order.get_orderlines();
			ev.stopPropagation();
			ev.preventDefault();
			var self = this
			$('.raghav').each(function(){
				var prod_id = parseInt(this.dataset.productId);
				for (var i = 0; i < self.optional_products.length; i++)
				{
					if(self.optional_products[i]['id'] == prod_id)
					{
						final_products.push(self.optional_products[i]);
					}
				}

			});
			var add = [];
			var new_prod = [self.props.product.id,final_products];
			if(self.env.pos.get('final_products')){
				add.push(self.env.pos.get('final_products'))
				add.push(new_prod)
				self.env.pos.set({
					'final_products': add,
				});
			}else{
				add.push(new_prod)
				self.env.pos.set({
					'final_products': add,
				});
			}
			var selected_line = null;
			if(self.update_line){
				orderlines.forEach(function (line) {
				if(line.selected == true){
					if(line.product.id == self.product.id)
					    {
						    selected_line = line;
						}
					}
				});
			if(selected_line != null){
					selected_line.set_combo_products(final_products)
				}else{
				    order.add_product(self.product);
				}
			}else{
				order.add_product(self.product);
			}
			self.trigger('close-popup');
		}
	}
	
	ProductComboSelectPopup.template = 'ProductComboSelectPopup';

	Registries.Component.add(ProductComboSelectPopup);

	return ProductComboSelectPopup;

});
