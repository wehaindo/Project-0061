odoo.define('weha_smart_pos_qris', function(require){

    const { register_payment_method, Payment } = require('point_of_sale.models');
    const PaymentQris = require('weha_smart_pos_qris.payment');
    const Registries = require('point_of_sale.Registries');
    
    register_payment_method('xendit_qris', PaymentQris);

    const PosPaymentQris = (Payment) => class PosPaymentQris extends Payment {
        constructor(obj, options) {
            super(...arguments);
        }
    }

    Registries.Model.extend(Payment, PosPaymentQris);
});