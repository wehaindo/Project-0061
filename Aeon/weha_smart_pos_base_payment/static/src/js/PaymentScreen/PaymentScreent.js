odoo.define('weha_smart_pos_base_payment.PaymentScreen', function(require) {
    "use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const { onMounted, useRef, useState } = owl;

    const BasePaymentScreen = PaymentScreen => class extends PaymentScreen {
        setup() {
            super.setup();
        }

        async _displayPaymentMethod() {
            await this.showPopup('PaymentMethodPopup', {
                parent: this,
                paymentMethods : this.payment_methods_from_config
            });
        }
    };

    Registries.Component.extend(PaymentScreen, BasePaymentScreen);
});