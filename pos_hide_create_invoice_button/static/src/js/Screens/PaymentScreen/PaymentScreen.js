odoo.define('pos_hide_create_invoice_button.PaymentScreen', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const {onMounted} = owl;

    const PaymentScreenInherit = PaymentScreen => class extends PaymentScreen {
        setup() {
            super.setup();
            // console.log("PaymentScreenInherit .....")
            onMounted(async () => {
                if (this.env.pos.config.invoice_visibility) {
                    let js_invoice = document.getElementsByClassName('js_invoice');
                    (js_invoice.length > 0) && (js_invoice[0].style.visibility = 'hidden');
                }
            })
        }
    };

    Registries.Component.extend(PaymentScreen, PaymentScreenInherit);

    return PaymentScreen;
});
