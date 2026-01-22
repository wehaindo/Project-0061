odoo.define('weha_smart_pos_aeon_pms.models', function(require){
    "use strict";

    var { PosCollection, PosGlobalState, Order, Orderline, Payment, PosModel } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const AeonMemberOrder = (Order) => 
        class extends Order {
            constructor(obj, options) {
                super(...arguments);
                this.is_aeon_member = this.is_aeon_member || false;                
                this.card_no = this.card_no || false;
                this.aeon_member = this.aeon_member || false;
                this.aeon_member_day = this.aeon_member_day || false;
                this.is_void_order = this.is_void_order || false;
            }

            init_from_JSON(json) {
                super.init_from_JSON(...arguments);
                this.is_aeon_member = json.is_aeon_member
                this.card_no = json.card_no;
                this.aeon_member = json.aeon_member;
                this.aeon_member_day = json.aeon_member_day;
                this.is_void_order = json.is_void_order;
            }
            
            export_as_JSON() {
                const json = super.export_as_JSON(...arguments);
                json.is_aeon_member = this.is_aeon_member
                json.card_no = this.card_no || false;
                json.aeon_member = this.aeon_member || false;
                json.aeon_member_day = this.aeon_member_day || false;
                json.is_void_order = this.is_void_order || false;
                return json;
            }

            set_is_aeon_member(is_aeon_member){
                this.is_aeon_member = is_aeon_member;
            }

            get_is_aeon_member(){
                return this.is_aeon_member;
            }

            set_aeon_member(aeon_member){
                this.aeon_member = aeon_member;
            }

            get_aeon_member(){
                return this.aeon_member;
            }

            set_aeon_member_day(aeon_member_day){
                this.aeon_member_day = aeon_member_day;
            }

            get_aeon_member_day(){
                return this.aeon_member_day;
            }

            set_card_no(card_no){
                this.card_no = card_no;
            }

            get_card_no(){
                return this.card_no;
            }

            clone(){
                const order = super.clone(...arguments);
                order.is_aeon_member = json.is_aeon_member
                order.card_no = this.card_no;
                order.aeon_member = this.aeon_member;
                order.aeon_member_day = this.aeon_member_day;
                return order;
            }
        }

    Registries.Model.extend(Order, AeonMemberOrder);

    class PaymentVoucher extends PosModel {
        constructor(obj, options) {
            super(obj);
            this.payment = options.payment;
            this.voucher_full = '';
            this.voucher_no = '';
            this.voucher_amount = '';
    
            if (options.json) {
                this.init_from_JSON(options.json);
                return;
            }
        }

        init_from_JSON(json){
            this.voucher_full = json.voucher_full;
            this.voucher_no = json.voucher_no;
            this.voucher_amount = json.voucher_amount;
        }

        set_voucher_full(voucher_full){
            this.voucher_full = voucher_full;
        }

        get_voucher_full(){
            return this.voucher_full;
        }

        set_voucher_no(voucher_no){
            this.voucher_no = voucher_no;
        }

        get_voucher_no(){
            return this.voucher_no;
        }

        set_voucher_amount(voucher_amount){
            this.voucher_amount = voucher_amount;
        }

        get_voucher_amount(){
            return this.voucher_amount;
        }

        export_as_JSON(){
            return {
                voucher_full: this.voucher_full,
                voucher_no: this.voucher_no,
                voucher_amount: this.voucher_amount,
            };
        }
    
    }

    Registries.Model.add(PaymentVoucher);
   
    
    const PmsPayment = (Payment) => 
        class extends Payment {
            constructor(obj, options) {
                super(...arguments);
                var self = this;
                this.voucherlines = this.voucherlines || new PosCollection();
            }

            init_from_JSON(json) {
                super.init_from_JSON(json);
                var self = this;
                // this.voucherlines = new PosCollection();                
                var voucherLines = json.voucherlines || [];
                for (var i = 0; i < voucherLines.length; i++) {
                    var voucherLine = voucherLines[i][2];
                    this.add_voucher_line(voucherLine);
                }
                console.log(this.voucherlines);
            }

            get_total_voucher() {
                return this.voucherlines.reduce((function(sum, voucherLine) {
                    sum += voucherLine.get_voucher_amount();
                    return sum;
                }), 0);
            }

            get_voucherlines(){
                return this.voucherlines;
            }

            add_voucher_line(voucherLine){
                var newvoucherline = PaymentVoucher.create({},{payment: this, json: voucherLine});
                this.voucherlines.add(newvoucherline);                
                return newvoucherline;            
            }
            
            export_as_JSON() {
                const json = super.export_as_JSON(...arguments);
                var voucherLines;
                voucherLines = [];
                this.voucherlines.forEach(_.bind(function(item) {
                    return voucherLines.push([0, 0, item.export_as_JSON()]);
                }, this));        
                json.voucherlines = voucherLines;
                return json;
            }

            clone(){
                const payment = super.clone(...arguments);
                return payment;
            }

        }
    
    Registries.Model.extend(Payment, PmsPayment);

    
    return {
        PaymentVoucher
    };
});