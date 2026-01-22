odoo.define('weha_smart_pos_base_payment.PaymentMethodPopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');

    class PaymentMethodPopup extends AbstractAwaitablePopup {
        /**
         * @param {Object} props
         * @param {string} props.startingValue
         */
        setup() {
            super.setup();
            this.parent = this.props.parent;
            this.paymentMethods = this.props.paymentMethods;
        }
    }
    PaymentMethodPopup.template = 'PaymentMethodPopup';
    PaymentMethodPopup.defaultProps = {
        cancelText: _lt('Back'),
        controlButtons: [],
        confirmKey: false,
    };

    Registries.Component.add(PaymentMethodPopup);

    return PaymentMethodPopup;
});