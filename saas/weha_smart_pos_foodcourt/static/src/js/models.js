odoo.define('weha_smart_pos_foodcourt.models', function (require) {
    "use strict";
    
    var models = require('point_of_sale.models');
    var { PosCollection, PosModel, PosGlobalState, Order, Orderline, Product } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    var utils = require('web.utils');
    var round_pr = utils.round_precision;
    var round_di = utils.round_decimals;
    var field_utils = require('web.field_utils');
    
    // models.load_fields("res.partner", ['remaining_wallet_amount', 'add_change_wallet']);
    // models.load_fields("pos.payment.method", ['allow_for_wallet']);

    const FoodcourtOrder = (Order) => 
    class extends Order {
        constructor(obj, options){
            super(...arguments);               
            this.used_amount_from_deposit = 0.00;
            this.client_remaining_deposit_amount = 0.00;
            this.to_deposit = false;
        }

        set_to_deposit(to_deposit){
            this.to_deposit = to_deposit;
        }
        
        is_to_deposit(){
            return this.to_wallet;
        }

        set_client_remaining_deposit_amount(amount){
            this.client_remaining_deposit_amount = val;
        }

        get_client_remaining_deposit_amount(){
            return this.client_remaining_deposit_amount;
        }

        set_type_for_deposit(type_for_deposit) {
            this.set('type_for_deposit', type_for_deposit);
        }

        get_type_for_deposit() {
            return this.get('type_for_deposit');
        }

        set_change_amount_for_deposit(change_amount_for_deposit) {
            this.set('change_amount_for_deposit', change_amount_for_deposit);
        }

        get_change_amount_for_deposit() {
            return this.get('change_amount_for_deposit') ? Number(this.get('change_amount_for_deposit')) : 0.00;
        }

        set_used_amount_from_deposit(used_amount_from_deposit) {
            this.used_amount_from_deposit = used_amount_from_deposit;
        }

        get_used_amount_from_deposit() {
            return this.used_amount_from_deposit;
        }

        export_as_JSON(){
            var orders = super.export_as_JSON();
            orders.deposit_type = this.get_type_for_deposit() || false;
            orders.amount_paid = this.get_total_paid() - (this.get_change() - Number(this.get_change_amount_for_deposit()));
            orders.amount_due = this.get_due() ? (this.get_due() + Number(this.get_change_amount_for_deposit())): 0.00;
            orders.change_amount_for_deposit= this.get_change_amount_for_deposit() || 0.00;
            orders.used_amount_from_deposit= this.get_used_amount_from_deposit() || false;
            orders.amount_return = this.get_change() - Number(this.get_change_amount_for_deposit());
            return orders;
        }

        export_for_printing(){
            const result = super.export_for_printing(...arguments);
            result.change_amount_for_deposit= this.get_change_amount_for_deposit() || false;
            result.used_amount_from_deposit= this.get_used_amount_from_deposit() || false;
            result.amount_paid= this.get_total_paid() - (this.get_change() - Number(this.get_change_amount_for_deposit()));
            result.amount_return= this.get_change() - Number(this.get_change_amount_for_deposit());
            result.amount_due= this.get_due() ? (this.get_due() + Number(this.get_change_amount_for_deposit())): 0.00;
            return result;
        }
    }
    
    Registries.Model.extend(Order, FoodcourtOrder);
})