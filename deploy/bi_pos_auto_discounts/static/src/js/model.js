odoo.define('aspl_pos_wallet.models', function (require) {
    "use strict";
    
        var models = require('point_of_sale.models');
        var utils = require('web.utils');
        var round_pr = utils.round_precision;
        var round_di = utils.round_decimals;
        var field_utils = require('web.field_utils');
    
        models.load_fields("res.partner", ['remaining_wallet_amount', 'add_change_wallet']);
        models.load_fields("pos.payment.method", ['allow_for_wallet']);
    
        var _super_Order = models.Order.prototype;
        models.Order = models.Order.extend({
            initialize: function(attributes,options){
                var res = _super_Order.initialize.apply(this, arguments);
                this.set({
                    change_amount_for_wallet: 0.00,
                    use_wallet: false,
                    type_for_wallet: false,
                });
                this.used_amount_from_wallet = 0.00;
                this.client_remaining_wallet_amount = 0.00;
                this.to_wallet = false;
                return this;
            },
            set_to_wallet: function(to_wallet){
                this.to_wallet = to_wallet;
            },
            is_to_wallet: function(){
                return this.to_wallet;
            },
            set_client_remaining_wallet_amount: function(val){
                this.client_remaining_wallet_amount = val;
            },
            get_client_remaining_wallet_amount: function(){
                return this.client_remaining_wallet_amount;
            },
            set_type_for_wallet: function(type_for_wallet) {
                this.set('type_for_wallet', type_for_wallet);
            },
            get_type_for_wallet: function() {
                return this.get('type_for_wallet');
            },
            set_change_amount_for_wallet: function(change_amount_for_wallet) {
                this.set('change_amount_for_wallet', change_amount_for_wallet);
            },
            get_change_amount_for_wallet: function() {
                return this.get('change_amount_for_wallet') ? Number(this.get('change_amount_for_wallet')) : 0.00;
            },
            set_used_amount_from_wallet: function(used_amount_from_wallet) {
                this.used_amount_from_wallet = used_amount_from_wallet;
            },
            get_used_amount_from_wallet: function() {
                return this.used_amount_from_wallet;
            },
            export_as_JSON: function(){
                var orders = _super_Order.export_as_JSON.call(this);
                orders.wallet_type = this.get_type_for_wallet() || false;
                orders.amount_paid = this.get_total_paid() - (this.get_change() - Number(this.get_change_amount_for_wallet()));
                orders.amount_due = this.get_due() ? (this.get_due() + Number(this.get_change_amount_for_wallet())): 0.00;
                orders.change_amount_for_wallet= this.get_change_amount_for_wallet() || 0.00;
                orders.used_amount_from_wallet= this.get_used_amount_from_wallet() || false;
                orders.amount_return = this.get_change() - Number(this.get_change_amount_for_wallet());
                return orders;
            },
            export_for_printing: function(){
                var orders = _super_Order.export_for_printing.call(this);
                orders.change_amount_for_wallet= this.get_change_amount_for_wallet() || false;
                orders.used_amount_from_wallet= this.get_used_amount_from_wallet() || false;
                orders.amount_paid= this.get_total_paid() - (this.get_change() - Number(this.get_change_amount_for_wallet()));
                orders.amount_return= this.get_change() - Number(this.get_change_amount_for_wallet());
                orders.amount_due= this.get_due() ? (this.get_due() + Number(this.get_change_amount_for_wallet())): 0.00;
                return orders;
            },
        });
    })