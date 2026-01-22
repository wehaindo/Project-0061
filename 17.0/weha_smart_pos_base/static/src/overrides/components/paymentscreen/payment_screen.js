/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { Component, useState, onMounted } from "@odoo/owl";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { PaymentMethodPopup } from "@weha_smart_pos_base/app/utils/payment_method_popup/payment_method_popup";

const { DateTime } = luxon;


patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
        onMounted(() => {
            const pendingPaymentLine = this.currentOrder.paymentlines.find(
                (paymentLine) =>
                    paymentLine.payment_method.use_payment_terminal === "deposit" &&
                    !paymentLine.is_done() &&
                    paymentLine.get_payment_status() !== "pending"
            );
            
            if (!pendingPaymentLine) {
                return;
            }

            pendingPaymentLine.set_payment_status('retry');
        });
    },
    async goToBackScreen(){
        var order = this.pos.get_order();
        if(order.get_is_deposit_order()){            
            const { confirmed } = await this.popup.add(ConfirmPopup, {
                title: _t("Rollback Topup Transaction"),
                body: _t("Topup transaction will cancelled. Do you want to continue?"),
            });
            if (confirmed) {               
                var lines = order.get_orderlines();        
                lines.filter(line => line.get_product())
                .forEach(line => order.removeOrderline(line));    
                order.set_is_deposit_order(false);
                this.pos.showScreen('ProductScreen');
            }
        }else{
            this.pos.showScreen('ProductScreen');
        }
    },   

    async addVoucher(){
        try {
            const { confirmed, payload: voucherCode } = await this.popup.add(TextInputPopup, {
                title: _t('Voucher Redeem'),
                placeholder: _t('Scan Voucher Code')
            });
            if (confirmed) {
                var order = this.pos.get_order();
                console.log(voucherCode);
                console.log(typeof(voucherCode));
                let domain = [['voucher_code','=', voucherCode]];
                const result = await this.orm.searchRead("pos.voucher", domain, []);
                console.log(result);
                var voucher = result[0]                           
                if (voucher){
                    var order_total_without_tax = order.get_total_without_tax();
                    var today = DateTime.now().toJSDate();
                    console.log(today);
                    // var expiry_date = moment(result['expiry_date']).format('YYYY-MM-DD');
                    var expiry_date = DateTime.fromFormat(voucher['expiry_date'], "yyyy-MM-dd");
                    console.log(expiry_date);
                    if(voucher['expiry_date'] && today > expiry_date){
                        this.env.services.popup.add(ErrorPopup, {
                            title: 'Voucher Redeem Error',
                            body: 'Voucher already expired',            
                        });                        
                    }
                    // else if(!voucher['is_active'] || voucher['state'] === 'used'){   
                    //     this.env.services.popup.add(ErrorPopup, {
                    //         title: 'Voucher Redeem Error',
                    //         body: 'Voucher not active',            
                    //     });
                    // } 
                    else if(voucher['state'] != 'open'){   
                        this.env.services.popup.add(ErrorPopup, {
                            title: 'Voucher Redeem Error',
                            body: 'Voucher cannot used',            
                        });
                    }                          
                    else if(voucher['minimum_purchase'] && 
                        result[0]['minimum_purchase'] > 0 &&
                        order_total_without_tax < voucher['minimum_purchase']){
                        this.env.services.popup.add(ErrorPopup, {
                            title: 'Voucher Redeem Error',
                            body: 'Total amount not enough',            
                        });
                    } 
                    else {
                        console.log('Voucher Valid');
                        var redeem_amount = Number(voucher['voucher_amount']);
                        var voucher_id = voucher['id'];
                        console.log(voucher_id);
                        if(this.pos.config.voucher_payment_method_id[0]){
                            var cashregisters = null;
                            for ( var j = 0; j <  this.pos.payment_methods.length; j++ ) {
                                if (this.pos.payment_methods[j].id === this.pos.config.voucher_payment_method_id[0]) {
                                    cashregisters = this.pos.payment_methods[j];
                                }
                                if (cashregisters) {                                    
                                    await this.orm.write("pos.voucher",[voucher_id],{state: 'used'});                                                                                                        
                                    order.add_paymentline(cashregisters);
                                    console.log(order.get_due());
                                    if(order.get_due() > redeem_amount){
                                        order.selected_paymentline.set_amount( Math.max(redeem_amount),0);
                                    }else{
                                        order.selected_paymentline.set_amount(order.get_due(false));
                                    }                                    
                                    order.selected_paymentline.set_is_voucher_payment(true);
                                    order.selected_paymentline.set_voucher_id(voucher_id);
                                    order.selected_paymentline.set_voucher_amount(Math.max(redeem_amount),0);                                    
                                    order.set_redeem_giftvoucher(result[0]);                                                                   
                                }
                            }                            
                        }
                    }                  
                }else{
                    this.env.services.popup.add(ErrorPopup, {
                        title: 'Voucher Redeem Error',
                        body: 'Voucher not Found',            
                    });
                }
            }
        } catch(err) {
            console.log(err);
        }
    },

    async showPaymentMethod(){
        const selectionList =  this.payment_methods_from_config.map((paymentMethod) => ({
            id: paymentMethod.id,
            label: paymentMethod.name,
            isSelected: false,
            item: paymentMethod,
        }))

        const { confirmed, payload: selectedPaymentMethod } = await this.popup.add(SelectionPopup, {
            title: _t("Select Payment Method"),
            list: selectionList,
        });

        if (confirmed) {
            this.addNewPaymentLine(selectedPaymentMethod);           
        }
    },
});