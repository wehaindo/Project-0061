odoo.define('weha_customer_deposit.models', function (require) {
    "use strict";
    
    var models = require('point_of_sale.models');
    var { PosCollection, PosModel, PosGlobalState, Order, Orderline, Product,Payment } = require('point_of_sale.models');
    var PaymentDeposit = require('weha_customer_deposit.PaymentDeposit');

    const Registries = require('point_of_sale.Registries');
    var utils = require('web.utils');
    
    models.register_payment_method('deposit', PaymentDeposit);

    const DepositOrder = (Order) =>
    class extends Order {
        constructor(obj, options) {
            super(...arguments);
            this.is_deposit_order = this.is_deposit_order || false;                
        }

        set_is_deposit_order(is_deposit_order){
            this.is_deposit_order = is_deposit_order
        }

        get_is_deposit_order(){
            return this.is_deposit_order;
        }

        add_product(product, options){
            if(this.get_is_deposit_order()){
                return
            }
            super.add_product(product,options);
        }

        remove_orderline( line ){        
            super.remove_orderline(line);
            if(this.orderlines.length == 0 && this.get_is_deposit_order()){
                this.set_is_deposit_order(false);
            }
        }

        init_from_JSON(json) {
            super.init_from_JSON(...arguments);
            this.is_deposit_order = json.is_deposit_order
        }
        
        export_as_JSON() {
            const json = super.export_as_JSON(...arguments);
            json.is_deposit_order = this.is_deposit_order
            return json;
        }

        clone(){
            const order = super.clone(...arguments);
            order.is_deposit_order = json.is_deposit_order
            return order;
        }
    }
     
    Registries.Model.extend(Order, DepositOrder);

    const DepositPayment = (Payment) => 
    class extends Payment {
        
        constructor(obj, options) {
            super(...arguments);
            this.terminal_id = this.terminal_id || '';
        }

        set_terminal_id(terminal_id){
            this.terminal_id = terminal_id;
        }

        init_from_JSON(json){
            this.terminal_id = json.terminal_id;
            super.init_from_JSON(...arguments);
        }
        
        export_as_JSON(){
            var json = super.export_as_JSON();            
            json.terminal_id = this.terminal_id;            
            return json;
        }
        
        clone(){
            var payment = super.clone();
            payment.terminal_id = this.terminal_id;
            return payment;
        }
    }

    Registries.Model.extend(Payment, DepositPayment);
})