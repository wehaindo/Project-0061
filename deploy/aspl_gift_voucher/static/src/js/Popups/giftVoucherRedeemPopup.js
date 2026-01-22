odoo.define('aspl_gift_voucher.giftVoucherRedeemPopup', function(require) {
    'use strict';

    const { useState, useRef } = owl;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;

    class giftVoucherRedeemPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            this.state = useState({ GiftVoucherNumber: '', GiftVoucherAmount:0.0, ShowMsg: false,});
        }
        async searchVoucher(){
            var self = this;
            self.state.ShowMsg = false;
            var order = self.env.pos.get_order();
            var today = moment().locale('en').format('YYYY-MM-DD');
            var code = self.state.GiftVoucherNumber;
            var params = {
                model: 'aspl.gift.voucher',
                method: 'search_read',
                domain: [['voucher_code', '=', code]],
            }
            await self.rpc(params, {async: false}).then(function(res){
                if(res.length > 0){
                    if (res[0]['redemption_order'] <= res[0]['redeem_voucher_count']) {
                        self.state.ShowMsg = "Gift voucher is expired!"
                    } else {
                        var expiry_date = moment(res[0]['expiry_date']).format('YYYY-MM-DD');
                        var order_total_without_tax = order.get_total_without_tax();
                        if(res[0]['expiry_date'] && today > expiry_date){
                            self.state.ShowMsg = "Gift Voucher is expired on " + res[0]['expiry_date'] + "!"
                           return;
                        } else if(!res[0]['is_active']){
                            self.state.ShowMsg = "Gift Voucher is not active!"
                            return;
                        } else if(res[0]['minimum_purchase'] && res[0]['minimum_purchase'] > 0 &&
                                                    order_total_without_tax < res[0]['minimum_purchase']){
                            self.state.ShowMsg = "Order amount is " + res[0]['minimum_purchase'] +  " or more for applying this Voucher!"
                            return;
                        } else if(res[0]['voucher_amount'] > order.get_due()) {
                            self.state.ShowMsg = "Voucher amount should not be above due amount!"
                            return
                        }else{
                            var voucherAmount = Number(res[0]['voucher_amount']);
                            self.state.GiftVoucherAmount = voucherAmount;
                        }
                    }
                }else{
                    self.state.ShowMsg = "Invalid gift voucher code!"
                }
            });
        }
        getPayload() {
            return {amount:this.state.GiftVoucherAmount, number:this.state.GiftVoucherNumber};
        }
    }
    giftVoucherRedeemPopup.template = 'giftVoucherRedeemPopup';
    giftVoucherRedeemPopup.defaultProps = {
        confirmText: 'Apply',
        cancelText: 'Cancel',
        title: '',
        body: '',
    };
    Registries.Component.add(giftVoucherRedeemPopup);
    return giftVoucherRedeemPopup;

});
