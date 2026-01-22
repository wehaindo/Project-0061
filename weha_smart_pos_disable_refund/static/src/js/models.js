odoo.define('weha_smart_pos_disable_refund.models', function(require){
    'use strict';

    var models = require('point_of_sale.models');
    var { PosCollection, PosModel, PosGlobalState, Order, Orderline, Product } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const RefundOrder = (Order) =>
        class extends Order {
            constructor(obj, options){
                super(...arguments);
                this.is_void = this.is_void || false;    
                this.is_refund = this.is_refund || false;           
                this.refund_parent_pos_reference = this.refund_parent_pos_reference || '';
                this.void_parent_pos_reference = this.void_parent_pos_reference || '';                 
                // this.reason = this.reason || '';
            }

            get_is_void(){
                return this.is_void;
            }

            set_is_void(is_void){
                this.is_void = is_void;
            }

            get_is_refund(){
                return this.is_refund;
            }

            set_is_refund(is_refund){
                this.is_refund = is_refund;
            }

            get_refund_parent_pos_reference(){
                return this.refund_parent_pos_reference;
            }

            set_refund_parent_pos_reference(refund_parent_pos_reference){
                this.refund_parent_pos_reference = refund_parent_pos_reference;
            }

            get_void_parent_pos_reference(){
                return this.void_parent_pos_reference;
            }

            set_void_parent_pos_reference(void_parent_pos_reference){
                this.void_parent_pos_reference = void_parent_pos_reference;
            }

            set_orderline_options(orderline, options){
                console.log("set_orderline_options");                
                console.log(orderline);
                console.log(options)
                super.set_orderline_options(...arguments);                
                console.log(orderline);
                orderline.set_price_source(options.price_source);                
                console.log(orderline);
            }

            // get_reason(){
            //     return this.reason;
            // }

            // set_reason(reason){
            //     this.reason = reason;
            // }

            clone(){
                const order = super.clone(...arguments);
                order.is_void = this.is_void;
                order.is_refund = this.is_refund;
                order.refund_parent_pos_reference = this.refund_parent_pos_reference;
                order.void_parent_pos_reference = this.void_parent_pos_reference;
                // order.reason = this.reason;
                return order;
            }

            init_from_JSON(json){
                super.init_from_JSON(...arguments);
                this.is_void = json.is_void;
                this.is_refund = json.is_refund;
                this.refund_parent_pos_reference = json.refund_parent_pos_reference;
                this.void_parent_pos_reference = json.void_parent_pos_reference;
                // this.reason = json.reason;
            }

            export_as_JSON(){
                const json = super.export_as_JSON(...arguments);
                json.is_void= this.is_void;
                json.is_refund=this.is_refund;
                json.refund_parent_pos_reference = this.refund_parent_pos_reference;
                json.void_parent_pos_reference = this.void_parent_pos_reference;
                // json.reason = this.reason;
                return json;
            }
            
            // export_for_printing(){
                
            // }
        }

    Registries.Model.extend(Order, RefundOrder);

    const RefundOrderline = (Orderline) =>
    class extends Orderline {
        set_quantity(quantity, keep_price){
            this.order.assert_editable();
            if(quantity === 'remove'){
                console.log("Clear Void and Refund Information");
                this.order.set_is_refund(false);
                this.order.set_is_void(false);
                this.order.set_refund_parent_pos_reference('');
                this.order.set_void_parent_pos_reference('');
            }
            super.set_quantity(quantity, keep_price);
            return true;
        }
    }

    Registries.Model.extend(Orderline, RefundOrderline);


});