odoo.define('mcs_pos_loyalty.screen', function (require) {
	"use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var _t = core._t;
    var rpc = require('web.rpc');
    var popup_widget = require('point_of_sale.popups');

    var field_utils = require('web.field_utils');
    var utils = require('web.utils');
    var round_pr = utils.round_precision;
    var framework = require('web.framework');

    models.load_fields('res.partner',['loyalty_id', 'date_of_birth']);

    var _super = models.Order;
    models.Order = models.Order.extend({

//        get_new_total_points: function() {
//            if (!this.pos.loyalty || !this.get_client()) {
//                return 0;
//            } else {
//                return round_pr(this.get_client().loyalty_points, this.pos.loyalty.rounding);
//            }
//        },

        get_new_points: function() {
            if (!this.pos.loyalty || !this.get_client()) {
                return 0;
            } else {
                return round_pr(this.loyalty_points || 0, this.pos.loyalty.rounding);
            }
        },
        get_burned_points: function() {
            if (!this.pos.loyalty || !this.get_client()) {
                return 0;
            } else {
                return round_pr(this.loyalty_burn_points || 0, this.pos.loyalty.rounding);
            }
        },
        get_new_total_points: function() {
            if (!this.pos.loyalty || !this.get_client()) {
                return 0;
            } else {
                return round_pr(this.get_client().loyalty_points, this.pos.loyalty.rounding);
            }
        },

        export_for_printing: function(){
            var json = _super.prototype.export_for_printing.apply(this,arguments);
            if (this.pos.loyalty && this.get_client()) {
                json.loyalty = {
                    rounding:     this.pos.loyalty.rounding || 1,
                    name:         this.pos.loyalty.name,
                    client:       this.get_client().name,
                    points_won  : this.get_new_points(),
                    points_spent: this.get_spent_points(),
                    points_total: this.get_new_total_points(),
                    points_burned: this.get_burned_points(),
                };
            }
            return json;
        },

        set_new_points: function(points){
            this.loyalty_points = points;
        },
        set_burned_points: function(points){
            this.loyalty_burn_points = points;
        },
        export_as_JSON: function(){
            var json = _super.prototype.export_as_JSON.apply(this,arguments);
            json.loyalty_burn_points = this.get_burned_points();
            return json;
        },

    });

	screens.ClientListScreenWidget.include({

        save_client_details: function(partner) {
        var self = this;

        var fields = {};
        this.$('.client-details-contents .detail').each(function(idx,el){
            if (self.integer_client_details.includes(el.name)){
                var parsed_value = parseInt(el.value, 10);
                if (isNaN(parsed_value)){
                    fields[el.name] = false;
                }
                else{
                    fields[el.name] = parsed_value
                }
            }
            else{
                fields[el.name] = el.value || false;
            }
        });

        if (!fields.loyalty_id) {
            if (!fields.phone) {
                if (!fields.name) {
                    this.gui.show_popup('error', _t('A Customer Name Is Required'));
                    return;
                }
                if (!fields.email) {
                    this.gui.show_popup('error', _t('An Email Is Required'));
                    return;
                }
                this.gui.show_popup('error', _t('Phone Number Is Required'));
                return;
            }
        }

        if (fields.phone) {
            if (fields.phone.charAt(0) == 0 || fields.phone.charAt(0) == "0") {
                fields.phone = ("62" + fields.phone.substring(1));
            }
        }

        if (this.uploaded_picture) {
            fields.image_1920 = this.uploaded_picture;
        }

        fields.id = partner.id || false;

        var contents = this.$(".client-details-contents");
        contents.off("click", ".button.save");


        rpc.query({
                model: 'res.partner',
                method: 'create_from_ui',
                args: [fields],
            })
            .then(function(partner_id){
                self.saved_client_details(partner_id);
            }).catch(function(error){
                error.event.preventDefault();
                var error_body = _t('Your Internet connection is probably down.');
                if (error.message.data) {
                    var except = error.message.data;
                    error_body = except.arguments && except.arguments[0] || except.message || error_body;
                }
                self.gui.show_popup('error',{
                    'title': _t('Error: Could not Save Changes'),
                    'body': error_body,
                });
                contents.on('click','.button.save',function(){ self.save_client_details(partner); });
            });
    },

        check_client_details: function(partner) {
            var self = this;
            rpc.query({
                model: 'res.partner',
                method: 'check_wallet_vernoss',
                args: [partner],
            })
            .then(function(partner_id){
                if (partner_id){
                    self.saved_client_details(partner_id);
                }
                else{
                    self.gui.show_popup('error',{
                        'title': _t('Error Vernoss'),
                        'body': "Loyalty ID not found!",
                    });
                }

            })
            .catch(function(error){
                error.event.preventDefault();
                var error_body = _t('Your Internet connection is probably down.');
                if (error.message.data) {
                    var except = error.message.data;
                    error_body = except.arguments && except.arguments[0] || except.message || error_body;
                }
                self.gui.show_popup('error',{
                    'title': _t('Error: Could not Check'),
                    'body': error_body,
                });
                contents.on('click','.button.check',function(){ self.check_client_details(partner); });
            });
        },
        display_client_details: function(visibility,partner,clickpos){
            this._super(visibility,partner,clickpos);

            var self = this;
            var contents = this.$('.client-details-contents');

            contents.off('click','.button.check');
            contents.on('click','.button.check',function(){ self.check_client_details(partner); });
        },
    });

    screens.PaymentScreenWidget.include({
        check_client_details: function() {
            var self = this;
            var order = this.pos.get_order();
            var serialized = order.export_as_JSON();
            var payment = this.pos.get_order().get_paymentlines();
            var list_payment = [];
            _.each(payment, function (each_payment) {
                list_payment.push(each_payment.export_as_JSON());
            });
            framework.blockUI();
            rpc.query({
                model: 'pos.order',
                method: 'sendEarnTransaction',
                args: [serialized, list_payment],
            })
            .then(function(result){
                if (result.point || result.point >= 0){
                    var client = self.pos.get_order().get_client();
                    if ( client ) {
                        client.loyalty_points = result.point;
                    }
                    self.pos.get_order().set_new_points(result.earn_points);
                    self.pos.get_order().set_burned_points(result.burned_points);
                    self.finalize_validation();
                }
                else{
                    if (result.burned_points || result.burned_points > 0){
                        self.pos.get_order().set_burned_points(result.burned_points);
                    }


                    self.gui.show_popup('confirm',{
                        'title': _t('Error'),
                        'body': _t('Are you sure to validate this payment? There is an error while burned or send earn transaction to Vernoss. With error message:')
                                + '\n' + result.responseMessage
                                + '\n' +  _t("Clicking 'Confirm' will validate this payment but the customer won't earn point."),
                        'confirm': function() {
                            self.validate_order('confirm');
                        },
                    });
                }

            framework.unblockUI();
            })
            .catch(function(error){
//                error.event.preventDefault();
                var error_body = _t('Your Internet connection is probably down.');
                if (error.message.data) {
                    var except = error.message.data;
                    error_body = except.arguments && except.arguments[0] || except.message || error_body;
                }
                self.gui.show_popup('error',{
                    'title': _t('Error: Could not Check to Vernos'),
                    'body': error_body,
                });

            framework.unblockUI();
            });
        },
        validate_order: function(force_validation) {
            if (this.order_is_valid(force_validation)) {

                var order = this.pos.get_order();

                if (!force_validation && order.get_won_points() > 0){
                    this.check_client_details();
                }
                else{
                    this.finalize_validation();
                }
            }

        }
    });

    var CustomLoyaltyPopup = popup_widget.extend({
        template: 'CustomLoyaltyPopup',
        show: function(){
            var self=this;
            this._super();

            var order = this.pos.get_order();
            var client = this.pos.get_client();

            var lines = order.get_orderlines();

            var redeemable_points = 0;

            rpc.query({
                model: 'res.partner',
                method: 'check_wallet_vernoss',
                args: [client, 'redeem'],
            })
            .then(function(loyalty_points){
                if (loyalty_points || String(loyalty_points)=='0'){ // Tambahan String(loyalty_points)=='0' agar yang punya loyalty id dan point nya 0 tidak error.
                    var available_point = loyalty_points ? loyalty_points : 0;

                    var total_order = order.get_due();
                    // console.log("order.get_due()")
                    // console.log(order.get_total_discount())

                    var client_points = self.$el[0].querySelector('.client_points');
                    client_points.innerHTML = available_point.toLocaleString();

                    redeemable_points = available_point > total_order ? total_order : available_point;
                    if (redeemable_points < 0){
                        redeemable_points = 0;
                    }

                    var client_redeemable_points = self.$el[0].querySelector('.client_redeemable_points');
                    client_redeemable_points.innerHTML = redeemable_points.toLocaleString();

                    $('#client_points_redeem').attr({"max" : redeemable_points});
                }
                else{
                    self.gui.show_popup('error',{
                        'title': _t('Error Vernoss'),
                        'body': "Loyalty ID not found!",
                    });
                }

            })
            .catch(function(error){
                var error_body = _t('Your Internet connection is probably down.');
                if (error.message.data) {
                    var except = error.message.data;
                    error_body = except.arguments && except.arguments[0] || except.message || error_body;
                }
                self.gui.show_popup('error',{
                    'title': _t('Error: Could not Check'),
                    'body': error_body,
                });

            });

            $('#client_points_redeem').on('change',function(e){
                if($(this).val() > redeemable_points){
                        self.gui.show_popup('alert',{
                        'title': _t('Warning'),
                        'body':  _t('Points redeem cannot be greater than redeemable points'),
                    });
                }
                if($(this).val() < 0){
                        self.gui.show_popup('alert',{
                        'title': _t('Warning'),
                        'body':  _t('Points redeem cannot be negative'),
                    });
                }
            })

            $('.custom_cancel').on('click',function(){
                self.gui.close_popup();
            });

            var rewards = order.get_available_rewards();
            var reward = rewards[0];
            // var product = null;
            rpc.query({
                model: 'product.product',
                method: 'get_product_by_id_with_available_pricelist',
                args: [reward.discount_product_id[0], self.pos.config.pricelist_id[0]],
            }).then(function (response) {
                console.log(response);
                let product_json = JSON.parse(response);                                               
                self.saveProductToStorage(product_json);                 
                var product_object = new models.Product({}, product_json);  
                self.pos.db.add_products([product_object]);                                       
                // self.product = self.pos.db.get_product_by_id(product_object.id);                                                                  
            }).catch(function(error){
                console.log(error);
                self.gui.show_popup('alert', {
                    title:  _t('Product Not Found'),
                    body:  _t('No product found for reward')
                });
                        
            });

            // var product   = this.pos.db.get_product_by_id(reward.discount_product_id[0]);
        
            $('.confirm_redeem').on('click',function(){                
                var discount = parseFloat($('#client_points_redeem').val());
                var product = self.pos.db.get_product_by_id(reward.discount_product_id[0]);
                console.log('confirm_redeem');
                console.log(product);
                
                if (!product) {
                    self.gui.close_popup();
                    self.gui.current_screen.order_widget.numpad_state.reset();
                }
                _.each(lines, function(line){
                    if(line && product){
                       if (product.id == line.product.id){
                            order.remove_orderline(line)
                       }
                    }
                });

                order.add_product(product, {
                    price: -discount,
                    quantity: 1,
                    merge: false,
                    extras: { reward_id: reward.id },
                });
                 self.gui.close_popup();
                 self.gui.current_screen.order_widget.numpad_state.reset();
            });

        },
        saveProductToStorage(product) {
            var request = indexedDB.open("OdooPOS", 1);            
            request.onsuccess = function (event) {
                var db = event.target.result;
                var transaction = db.transaction(["products"], "readwrite");
                var store = transaction.objectStore("products");
                store.put(product);
                console.log("Products saved to IndexedDB!");
            };
            
        },
    });

    gui.define_popup({ name: 'custom_loyalty', widget: CustomLoyaltyPopup });

    gui.Gui.include({
        numpad_input: function(buffer, input, options) {
            var newbuf  = buffer.slice(0);
            options = options || {};
            var newbuf_float  = newbuf === '-' ? newbuf : field_utils.parse.float(newbuf);
            var decimal_point = _t.database.parameters.decimal_point;
            if (input === decimal_point) {
                if (options.firstinput) {
                    newbuf = "0.";
                }else if (!newbuf.length || newbuf === '-') {
                    newbuf += "0.";
                } else if (newbuf.indexOf(decimal_point) < 0){
                    newbuf = newbuf + decimal_point;
                }
            } else if (input === 'CLEAR') {
                newbuf = "";
            } else if (input === 'BACKSPACE') {
                newbuf = newbuf.substring(0,newbuf.length - 1);
            } else if (input === '+') {
                if ( newbuf[0] === '-' ) {
                    newbuf = newbuf.substring(1,newbuf.length);
                }
            } else if (input === '-') {
                if (options.firstinput) {
                    newbuf = '-0';
                } else if ( newbuf[0] === '-' ) {
                    newbuf = newbuf.substring(1,newbuf.length);
                } else {
                    newbuf = '-' + newbuf;
                }
            } else if (input[0] === '+' && !isNaN(parseFloat(input))) {
                newbuf = this.chrome.format_currency_no_symbol(newbuf_float + parseFloat(input));
            }else if (input[0] === '*' && !isNaN(parseFloat(input.substring(1,input.length)))) {
                newbuf = this.chrome.format_currency_no_symbol(newbuf_float * parseFloat(input.substring(1,input.length)));
            } else if (!isNaN(parseInt(input))) {
                if (options.firstinput) {
                    newbuf = '' + input;
                } else {
                    newbuf += input;
                }
            }
            if (newbuf === "-") {
                newbuf = "";
            }

            // End of input buffer at 12 characters.
            if (newbuf.length > buffer.length && newbuf.length > 12) {
                this.play_sound('bell');
                return buffer.slice(0);
            }

            return newbuf;
        },
    });

//    var LoyaltyButton = screens.ActionButtonWidget.extend({
//        template: 'LoyaltyButton',
//        button_click: function(){
//            var order  = this.pos.get_order();
//            var client = order.get_client();
//            if (!client) {
//                this.gui.show_screen('clientlist');
//                return;
//            }
//
//            var rewards = order.get_available_rewards();
//            if (rewards.length === 0) {
//                this.gui.show_popup('alert',{
//                    'title': _t('No Rewards Available'),
//                    'body':  _t('There are no rewards available for this customer as part of the loyalty program'),
//                });
//                return;
//            }
//            else {
//                var list = [];
//                for (var i = 0; i < rewards.length; i++) {
//                    list.push({
//                        label: rewards[i].name,
//                        item:  rewards[i],
//                    });
//                }
//                this.gui.show_popup('custom_loyalty', {
//                    'title': _t("Customize Loyalty"),
//                });
//            }
//        },
//    });

//    screens.define_action_button({
//        'name': 'loyalty',
//        'widget': LoyaltyButton,
//        'condition': function(){
//            return this.pos.loyalty && this.pos.loyalty.rewards.length;
//        },
//    });

    






    // Yayat, export function biar bisa diextend
    return{
        CustomLoyaltyPopup:CustomLoyaltyPopup
    }
});