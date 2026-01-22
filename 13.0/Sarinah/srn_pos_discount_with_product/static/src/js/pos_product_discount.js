
// srn_pos_discount_with_product
odoo.define('srn_pos_discount_with_product.pos_product_discount', function (require) {
    "use strict";
    // console.log('loaded')
    var screens = require('point_of_sale.screens'); // harus direquired jika ingin extend function dimodels
    var models = require('point_of_sale.models');
    var rpc = require('web.rpc');
    // global variable for store order that have srn_product_discount, Untuk Cara 1
    // var glob_product_discount_order = {}

    // screens.ProductScreenWidget.include({
    //     // handle when product clicked on the screen
    //     click_product: function (product) {
    //         console.log('click_product');
    //         // return;
    //         this._super(product);
    //     }
    // });

    // screens.ProductCategoriesWidget.include({
    //     // handle when typing on searching box and hit enter
    //     perform_search: function(category, query, buy_result){
    //         if(buy_result){
    //             console.log('performe_search');
    //         }
    //         // return;
    //         this._super(category, query, buy_result);
    //     }
    // });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        add_product: function (product, options){
            // product == arguments
            // console.log('start add_product');
            // console.log('product');
            // console.log(product);
            // console.log('options');
            // console.log(options);
            // console.log('this');
            // console.log(this);
            // console.log('arguments');
            // console.log(arguments);
            // _super_order.add_product.apply(this,arguments);
            // console.log('add_product end');
            
            // console.log('test print self')
            // console.log(self)
            // console.log('test print this')
            // console.log(this)
            // console.log('test print super order')
            // console.log(_super_order)
            // console.log(my_this.get_orderlines())
            // _super_order.add_product.apply(my_this, arguments);
            
            
            var my_this = this;
            // current order
            var current_order = my_this; // this sudah dipindah ke self di gift_voucher module
            // current sku
            var current_sku = product?.default_code;

            var model = 'srn.pos.product.discount';
            var domain = [['active', '=', true], ['sku', '=', current_sku]];
            var fields = [];

            // DCDWP -> DISCOUNT WITH PRODUCT
            if(current_sku){
                if(current_sku.toUpperCase().includes('DCDWP')){
                    if(options?.is_checked_product_discount){
                        _super_order.add_product.apply(this, arguments);

                        // set price_manually_set = true to last_order line
                        if(options?.price_manually_set){
                            var last_order_line = current_order.get_last_orderline();
                            if(last_order_line){
                                last_order_line.price_manually_set = true;
                            }
                        }
                        console.log('srn_pos_discount_with_product - Final Execution');
                        // console.log(arguments)
                    }else{
                        rpc.query({
                            model: model,
                            method: 'search_read',
                            args: [domain, fields]
                        }).then(function (data) {
                            if (data.length > 0) {
                                // this is the condition where current input sku is part of product_discount

                                // Cara 1. remove order line that have product_discount if any, NOTE: using find will only return one element of array (first found)
                                // var order_line_has_to_remove = current_order.get_orderlines().find(({product}) => product?.default_code == glob_product_discount_order[current_order['cid']]?.sku);
                                // if(order_line_has_to_remove != undefined){
                                //     current_order.remove_orderline(order_line_has_to_remove);
                                // }
                                
                                // Cara 2. remove order line that contains DCDWP on SKU
                                var order_line_has_to_remove = current_order.get_orderlines().find(({product}) => product?.default_code.toUpperCase().includes('DCDWP'));
                                if(order_line_has_to_remove != undefined){
                                    current_order.remove_orderline(order_line_has_to_remove);
                                }

                                
                                // remove flag for global variable that orders have product_discount, Untuk Cara 1
                                // delete(glob_product_discount_order[current_order['cid']]);

                                // calculate the price
                                var subtotal = current_order.get_subtotal();

                                var disc_percentage = parseInt(data[0]?.disc_percentage > 0 ? data[0]?.disc_percentage : 100);
                                var max_disc = parseInt(data[0]?.max_discount) == 0 ? subtotal : parseInt(data[0]?.max_discount);
                                var is_only_normal_price = data[0]?.only_normal_price;
                                var min_transaction = data[0]?.minimum_transaction;

                                // calculation for normal price only
                                if(is_only_normal_price){
                                    subtotal = 0;
                                    // filter order lines , only that contains discount
                                    current_order.get_orderlines().filter((element) => {
                                        if(element?.custom_discount_id == null && element?.custom_promotion_id == null && element?.price > 0){
                                            // calculate subtotal
                                            subtotal += (element.quantity * element.price);
                                        }
                                    });
                                }

                                // filter minimum transaction (subtotal)
                                if(subtotal >= min_transaction){

                                    // calculation amount of discount
                                    subtotal = subtotal * (disc_percentage / 100);
                                    
                                    // apply max allowed amount of discount
                                    if(subtotal >= max_disc){
                                        subtotal = max_disc;
                                    }
                                    
                                    // set flag for global variable that orders have product_discount, Untuk Cara 1
                                    // glob_product_discount_order[current_order['cid']] = { sku: current_sku }

                                    // add product to the cart
                                    current_order.add_product(product, { quantity: 1, price: parseInt(-1 * subtotal), merge:false, price_manually_set: true, is_checked_product_discount:true });

                                    console.log('srn_pos_discount_with_product - Checked and Found');
                                }else{
                                    console.log('srn_pos_discount_with_product - Checked and Found - Sub Total Less than Minimum Transaction');
                                    current_order.add_product(product, { quantity: 1, price: 0, merge:false, price_manually_set: true, is_checked_product_discount:true});
                                }

                            }else{
                                console.log('srn_pos_discount_with_product - Checked and Not Found');
                                current_order.add_product(product, {is_checked_product_discount:true});
                            }

                        });
                    }
                }else{
                    _super_order.add_product.apply(this, arguments);
                }
            }else{ _super_order.add_product.apply(this, arguments); }
        }
    });
});
