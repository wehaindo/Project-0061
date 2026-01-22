odoo.define('weha_customer_deposit.PaymentScreen', function(require) {

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');      
    const { useListener } = require("@web/core/utils/hooks");
    const utils = require('web.utils');
    const { onMounted } = owl;      

    const DepositPaymentScreen = PaymentScreen =>class extends PaymentScreen {

        setup() {   
            super.setup();
            useListener('check-payment-deposit', this._checkDepositPayment);
            onMounted(() => {
                const pendingPaymentLine = this.currentOrder.paymentlines.find(
                    paymentLine => paymentLine.payment_method.use_payment_terminal === 'deposit' &&
                        (!paymentLine.is_done() && paymentLine.get_payment_status() !== 'pending')
                );
                if (pendingPaymentLine) {    
                    const paymentTerminal = pendingPaymentLine.payment_method.payment_terminal;
                    if(pendingPaymentLine.get_payment_status() != 'waiting_deposit'){                
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

        async _checkDepositPayment({ detail: line }){
            const payment_terminal = line.payment_method.payment_terminal;
            line.set_payment_status('waiting');
            const isPaymentSuccessful = await payment_terminal.check_payment_deposit(line.cid);
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
                line.set_payment_status('waiting_deposit');
            }
        }
    }

    Registries.Component.extend(PaymentScreen, DepositPaymentScreen);

    return PaymentScreen;
});
