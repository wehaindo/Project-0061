odoo.define('weha_smart_pos_bca_edc.PaymentScreen', function(require) {
    "use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const { onMounted, useRef, useState } = owl;

    const BcaEdcPosPaymentScreen = PaymentScreen => class extends PaymentScreen {
        setup() {
            super.setup();
            onMounted(() => {
                const pendingPaymentLine = this.currentOrder.paymentlines.find(
                    paymentLine => paymentLine.payment_method.use_payment_terminal === 'bca_edc' &&
                        (!paymentLine.is_done() && paymentLine.get_payment_status() !== 'pending')
                );
                if (pendingPaymentLine) {
                    const paymentTerminal = pendingPaymentLine.payment_method.payment_terminal;
                    pendingPaymentLine.set_payment_status('waiting');
                    // paymentTerminal.start_get_status_polling().then(isPaymentSuccessful => {
                    //     if (isPaymentSuccessful) {
                    //         pendingPaymentLine.set_payment_status('done');
                    //         pendingPaymentLine.can_be_reversed = paymentTerminal.supports_reversals;
                    //     } else {
                    //         pendingPaymentLine.set_payment_status('retry');
                    //     }
                    // });
                }
            });
        }
    };

    Registries.Component.extend(PaymentScreen, BcaEdcPosPaymentScreen);
});