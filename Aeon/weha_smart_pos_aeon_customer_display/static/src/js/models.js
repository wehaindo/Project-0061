odoo.define('weha_smart_pos_aeon_customer_display.models', function(require){
    'use strict';

    var { PosGlobalState, Order } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const CustomerDisplayPosGlobalState = (PosGlobalState) => 
    class  extends PosGlobalState {
        constructor(obj) {
            super(obj);
        }

        send_current_order_to_customer_facing_display() {
            var self = this;
            var order = this.get_order();            
            var orderLines = []
            console.log(order);
            order.get_orderlines().forEach(function (orderline) {
                console.log(orderline);
                var orderline = {
                    name : orderline.product.display_name,
                    qty : orderline.quantity,
                    price_source: orderline.get_price_source(),            
                    price_unit: orderline.list_price,                    
                    price_unit_str: self.format_currency_no_symbol(orderline.list_price),
                    promo_discount_str: self.format_currency_no_symbol((orderline.list_price - orderline.price) * orderline.get_quantity()),
                    discount_type: orderline.get_discount_type(),
                    discount_str: orderline.get_discount_str(),
                    price_subtotal_incl: orderline.get_quantity() * orderline.get_list_price(),
                    price_subtotal_incl_str: self.format_currency_no_symbol( orderline.get_quantity() * orderline.get_list_price())
                }    
                orderLines.push(orderline);
            });
            var data = {
                actionType: 'updateOrderUi',
                message :{                
                    orderLines: orderLines,
                    total_without_discount : order.get_total_without_discount(),
                    total_without_discount_str : this.format_currency_no_symbol(order.get_total_without_discount()),
                    total_with_tax: order.get_total_with_tax(),
                    total_with_tax_str: this.format_currency_no_symbol(order.get_total_with_tax()),
                    total_discount: order.get_total_discount(),
                    total_discount_str: this.format_currency_no_symbol(order.get_total_discount())
                }
            }
            fetch("http://localhost:8001/customerdisplay", {
                method: "POST",
                body: JSON.stringify(data),
                headers: {
                  "Content-type": "application/json; charset=UTF-8"
                }
            }).catch((error) => {
                console.log(error);
            });


        }

        send_prima_qrcode_to_customer_facing_display(qrcode){
            var self = this;
            var data = {
                actionType: 'primaQrCode',
                message :{                
                    qrcode: qrcode                    
                }
            }
            fetch("http://localhost:8001/customerdisplay", {
                method: "POST",
                body: JSON.stringify(data),
                headers: {
                  "Content-type": "application/json; charset=UTF-8"
                }
            }).catch((error) => {
                console.log(error);
            });
        }

        send_prima_qrcode_cancel_to_customer_facing_display(){
            var self = this;
            var data = {
                actionType: 'primaQrCodeClear',
                message :{}
            }
            fetch("http://localhost:8001/customerdisplay", {
                method: "POST",
                body: JSON.stringify(data),
                headers: {
                  "Content-type": "application/json; charset=UTF-8"
                }
            }).catch((error) => {
                console.log(error);
            });
        }        
    }

    Registries.Model.extend(PosGlobalState, CustomerDisplayPosGlobalState);

    const CustomerDisplayOrder = (Order) => 
    class extends Order {	
        constructor(obj, options) {
            super(obj, options);            
        }

        get_total_without_discount(){
            var total_without_discount = 0;
            this.orderlines.forEach(function(orderline){
                total_without_discount = total_without_discount + (orderline.get_quantity() * orderline.get_list_price());
            })

            return total_without_discount;
        }

        get_totalitem(){
            return this.orderlines.length;
        }

        get_totalquantity(){
            var totalquantity = 0;
            this.orderlines.forEach(function(orderline){
                totalquantity = totalquantity + orderline.get_quantity();
            });

            return totalquantity;
        }
    }

    Registries.Model.extend(Order, CustomerDisplayOrder);
});