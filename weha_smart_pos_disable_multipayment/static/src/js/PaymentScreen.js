odoo.define('weha_smart_pos_disable_multipayment.PaymentScreen', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    const WehaPaymentScreen = PaymentScreen =>
        class extends PaymentScreen {
            addNewPaymentLine({ detail: paymentMethod }) {
                // Get current order payment lines
                const existingPaymentLines = this.currentOrder.get_paymentlines();
                
                // Check if payment method type already exists
                const duplicateExists = existingPaymentLines.some(line => 
                    line.payment_method.type === paymentMethod.type
                );
                
                if (duplicateExists) {
                    // Show popup warning
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Duplicate Payment Method Type'),
                        body: this.env._t(`A payment line with "${paymentMethod.type}" payment method type already exists. You cannot add multiple payment lines with the same payment method type.`),
                    });
                    return false;
                }
                
                // If no duplicate, proceed with adding the payment line
                return super.addNewPaymentLine({ detail: paymentMethod });
            }
        };

    Registries.Component.extend(PaymentScreen, WehaPaymentScreen);

    return PaymentScreen;
});