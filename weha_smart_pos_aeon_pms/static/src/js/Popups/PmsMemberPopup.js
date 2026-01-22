odoo.define('weha_smart_pos_aeon_pms.PmsMemberPopup', function(require) {
    'use strict';

    const { onMounted, useRef, useState } = owl;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;


    class PmsMemberPopup extends AbstractAwaitablePopup {
        setup() {
            super.setup();
            var order = this.env.pos.get_order();
            console.log(order);
            console.log(order.get_is_aeon_member());
            this.state = useState({ CustomerNumber: '', CustomerInfo: '', IsAeonMember: false, ShowMsg: false, Valid: false});
            this.state.CustomerNumber = order.get_aeon_member();
            this.state.IsAeonMember = order.get_is_aeon_member();
            this.customerNumberRef = useRef('customernumber');
            this.confirmButtonRef = useRef('confirmbutton');
            onMounted(this.onMounted);
        }

        onMounted() {
            this.customerNumberRef.el.focus();            
        }

        async searchCustomer(){
            // 5 2 3 0 0 0 0 0 0 9 0 0 0 0 0 2 3 0 2 1 3
            // 523000000900001230213
            // 523000000900000230213
            //  
            
            var self = this;
            this.state.ShowMsg = false;
            var code = self.state.CustomerNumber;
            if(code.length != 21){
                this.state.Valid = false;
                this.state.ShowMsg = 'Customer number not valid!';
            }else{
                var discountActive = code.substring(14,15);
                var cardNO = code.substring(0,14);
                // var card_no = "52600001400000"
                var mobile = ""
                var IDCard = ""
                var merchant_id = "01"
                await this.rpc({
                    model: 'res.partner',
                    method: 'pms_check_member',
                    args: ['',cardNO, mobile, IDCard, merchant_id],
                }).then(function (result) {
                    console.log('result');
                    // console.log(result);
                    var result_json = result;
                    // var result_json = JSON.parse(result)   
                    // var result_json = result.data[0];
                    console.log(result_json);               
                    var order = self.env.pos.get_order();
                    // if(result_json.err == false){
                    if(result_json.err == false){
                        self.state.CustomerInfo =  result_json.data[0].nick_name;
                    }else{
                        self.state.CustomerInfo = cardNO;
                    }
                    self.state.Valid = true;                    
                    order.set_is_aeon_member(true);
                    order.set_aeon_member(code);
                    order.set_aeon_customer_name(result_json.data[0].nick_name);
                    order.set_aeon_customer_email(result_json.data[0].Email);
                    console.log("Set Card No");
                    order.set_card_no(cardNO);
                    if (discountActive === '1'){
                        order.set_aeon_member_day(true);
                    }else{
                        order.set_aeon_member_day(false);
                    }
                });       
            }
        }

        clearCustomer(){
            var self = this;
            var order = self.env.pos.get_order();
            // Reset Display
            self.state.IsAeonMember = false;
            self.state.CustomerNumber = "";
            self.state.CustomerInfo = "";
            self.state.ShowMsg = false;
            self.state.Valid = false;
            // Clear Order
            order.set_is_aeon_member(false);
            order.set_aeon_member("");
            order.set_card_no("");
            order.set_aeon_member_day(false);            
        }

        getPayload() {
            return {amount:this.state.VoucherAmount, number:this.state.VoucherNumber};
        }
    }

    PmsMemberPopup.template = 'PmsMemberPopup';
    PmsMemberPopup.defaultProps = {
        confirmText: 'Apply',
        cancelText: 'Cancel',
        title: '',
        body: '',
    };
    Registries.Component.add(PmsMemberPopup);
    return PmsMemberPopup;

});
