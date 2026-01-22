odoo.define('weha_smart_pos_aeon_prima.PaymentScreen', function(require) {
    "use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");
    const utils = require('web.utils');
    const { onMounted } = owl;

    const PrimaQrisPaymentScreen = PaymentScreen => class extends PaymentScreen {
        setup() {   
            super.setup();
            useListener('check-payment-prima-qris', this._checkPaymentPrimaQris);
            onMounted(() => {
                const pendingPaymentLine = this.currentOrder.paymentlines.find(
                    paymentLine => paymentLine.payment_method.use_payment_terminal === 'prima' &&
                        (!paymentLine.is_done() && paymentLine.get_payment_status() !== 'pending')
                );
                if (pendingPaymentLine) {    
                    const paymentTerminal = pendingPaymentLine.payment_method.payment_terminal;
                    pendingPaymentLine.set_payment_status('waiting_prima_qris');
                    // if(pendingPaymentLine.get_payment_status() != 'waiting_prima_qris'){                
                    //     pendingPaymentLine.set_payment_status('waiting');
                    //     paymentTerminal.start_get_status_polling().then(isPaymentSuccessful => {
                    //         if (isPaymentSuccessful) {
                    //             pendingPaymentLine.set_payment_status('done');
                    //             pendingPaymentLine.can_be_reversed = paymentTerminal.supports_reversals;
                    //         } else {
                    //             pendingPaymentLine.set_payment_status('retry');
                    //         }
                    //     });
                    // }
                }
            });
        }

        async _checkPaymentPrimaQris({ detail: line }){
            const payment_terminal = line.payment_method.payment_terminal;
            line.set_payment_status('waiting');
            const isPaymentSuccessful = await payment_terminal.check_payment_prima_qris(line.cid);
            if (isPaymentSuccessful) {
                line.set_payment_status('done');
                line.can_be_reversed = payment_terminal.supports_reversals;
                if (
                    this.currentOrder.is_paid() &&
                    utils.float_is_zero(this.currentOrder.get_due(), this.env.pos.currency.decimal_places)
                ) {
                    this.trigger('validate-order');
                }
            } else {
                line.set_payment_status('waiting_qris');
            }
        }

        async deletePaymentLine(event) {
            const { confirmed } = await this.showPopup('ConfirmPopup', {
                title: 'Delete Payment',
                body: 'Do you want to remove this payment ?',
            });
            if(confirmed){
                super.deletePaymentLine(event);
                this.env.pos.send_prima_qrcode_cancel_to_customer_facing_display();
            }
        }

        get nextScreen() {
            var next = super.nextScreen;
            if (next === 'ReceiptScreen'){
                this.env.pos.send_prima_qrcode_cancel_to_customer_facing_display();
            }
            return next;
        }
    };

    Registries.Component.extend(PaymentScreen, PrimaQrisPaymentScreen);

  
});
