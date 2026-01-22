import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { onMounted } from "@odoo/owl";

patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
        onMounted(async () => {
            const pendingPaymentLine = this.currentOrder.payment_ids.find(
                (paymentLine) =>
                    paymentLine.payment_method_id.use_payment_terminal === "bcaecrpay" &&
                    !paymentLine.is_done() &&
                    paymentLine.get_payment_status() !== "pending"
            );
            if (pendingPaymentLine) {
                const paymentTerminal = pendingPaymentLine.payment_method.payment_terminal;
                if(pendingPaymentLine.get_payment_status() != 'waiting_bcaecr'){                
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
    },
});


patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
        onMounted(async () => {
            const pendingPaymentLine = this.currentOrder.payment_ids.find(
                (paymentLine) =>
                    paymentLine.payment_method_id.use_payment_terminal === "bcaecrmanualpay" &&
                    !paymentLine.is_done() &&
                    paymentLine.get_payment_status() !== "pending"
            );
            if (pendingPaymentLine) {
                const paymentTerminal = pendingPaymentLine.payment_method.payment_terminal;
                if(pendingPaymentLine.get_payment_status() != 'waiting_bcaecrmanualpay'){                
                    pendingPaymentLine.set_payment_status('waitingInput');
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
    },
});