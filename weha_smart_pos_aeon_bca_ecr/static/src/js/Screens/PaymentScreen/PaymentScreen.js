odoo.define('weha_smart_pos_aeon_bca_ecr.PaymentScreen', function(require) {
    "use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");
    const utils = require('web.utils');
    const { onMounted } = owl;

    const BcaEcrPaymentScreen = PaymentScreen => class extends PaymentScreen {
        setup() {   
            super.setup();
            useListener('check-payment-qris', this._checkQrisPayment);
            onMounted(() => {
                const pendingPaymentLine = this.currentOrder.paymentlines.find(
                    paymentLine => paymentLine.payment_method.use_payment_terminal === 'bcaecr' &&
                        (!paymentLine.is_done() && paymentLine.get_payment_status() !== 'pending')
                );
                if (pendingPaymentLine) {    
                    const paymentTerminal = pendingPaymentLine.payment_method.payment_terminal;
                    if(pendingPaymentLine.get_payment_status() != 'waiting_qris'){                
                        pendingPaymentLine.set_payment_status('waiting');
                        paymentTerminal.start_get_status_polling().then(isPaymentSuccessful => {
                            if (isPaymentSuccessful) {
                                pendingPaymentLine.set_payment_status('done');
                                pendingPaymentLine.can_be_reversed = paymentTerminal.supports_reversals;
                            } else {
                                pendingPaymentLine.set_payment_status('retry');
                            }
                        });
                    }
                }
            });
        }

        async _checkQrisPayment({ detail: line }){
            const payment_terminal = line.payment_method.payment_terminal;
            line.set_payment_status('waiting');
            const isPaymentSuccessful = await payment_terminal.check_payment_qris(line.cid);
            if (isPaymentSuccessful) {
                line.set_payment_status('done');
                line.can_be_reversed = payment_terminal.supports_reversals;
                // Automatically validate the order when after an electronic payment,
                // the current order is fully paid and due is zero.
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
    };

    Registries.Component.extend(PaymentScreen, BcaEcrPaymentScreen);

    const BankManualPaymentScreen = PaymentScreen => class extends PaymentScreen {
        setup() {   
            super.setup();
            useListener('input-manual-popup', this._inputManualPopup);

            onMounted(() => {
                console.log('mounted BankManualPaymentScreen');
                const pendingPaymentLine = this.currentOrder.paymentlines.find(
                    paymentLine => paymentLine.payment_method.use_payment_terminal === 'bankmanual' &&
                        (!paymentLine.is_done() && paymentLine.get_payment_status() == 'pending')
                );
                if (pendingPaymentLine) {    
                    const paymentTerminal = pendingPaymentLine.payment_method.payment_terminal;
                    pendingPaymentLine.set_payment_status('waiting_manual_input');                
                }
            });
        }

        async _inputManualPopup({ detail: line}){
            const { confirmed, payload: cardinfo } = await this.showPopup('BankManualPopup', {});
            if (confirmed) {
                console.log('confirm');
                console.log(cardinfo);
                line.set_pan(cardinfo.cardnumber);
                line.set_expired_date(cardinfo.expireddate);
                line.set_approval_code(cardinfo.approvalcode);
                line.set_merchant_id(cardinfo.merchantcode);
                line.set_terminal_id(cardinfo.terminalid);
                line.set_payment_status('');
            }
        }
    }

    Registries.Component.extend(PaymentScreen, BankManualPaymentScreen);

    const QrisManualPaymentScreen = PaymentScreen => class extends PaymentScreen {
        setup() {   
            super.setup();
            useListener('input-qris-popup', this._inputQrisPopup);

            onMounted(() => {
                console.log('mounted QrisManualPaymentScreen');
                const pendingPaymentLine = this.currentOrder.paymentlines.find(
                    paymentLine => paymentLine.payment_method.use_payment_terminal === 'qrismanual' &&
                        (!paymentLine.is_done() && paymentLine.get_payment_status() == 'pending')
                );
                if (pendingPaymentLine) {    
                    const paymentTerminal = pendingPaymentLine.payment_method.payment_terminal;
                    pendingPaymentLine.set_payment_status('waiting_qris_input');                
                }
            });
        }

        async _inputQrisPopup({ detail: line}){
            const { confirmed, payload: cardinfo } = await this.showPopup('QrisManualPopup', {});
            if (confirmed) {
                console.log('confirm');
                console.log(cardinfo);
                line.set_approval_code(cardinfo.approvalcode);
                line.set_merchant_id(cardinfo.merchantcode);
                line.set_terminal_id(cardinfo.terminalid);
                line.set_payment_status('');
            }
        }
    }

    Registries.Component.extend(PaymentScreen, QrisManualPaymentScreen);    

    return PaymentScreen;
});
