odoo.define('weha_smart_pos_foodcourt.PaymentDepositPopup', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    class PaymentDepositPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            this.state = useState({ inputchange: this.props.change});
            this.change = useRef('change');
        }
        getPayload(){
            var order = this.env.pos.get_order();
            if(order.get_client()){
                order.set_type_for_deposit('change');
                order.set_change_amount_for_deposit(order.get_change());
            }
        }
        on_skip(){
           this.props.resolve({ skip: true });
           this.trigger('close-popup');
        }
        cancel(){
            this.trigger('close-popup');
        }
    }
    PaymentDepositPopup.template = 'PaymentDepositPopup';

    PaymentDepositPopup.defaultProps = {
        confirmText: 'Add to Deposit',
        skipText: 'Skip',
        cancelText: 'Cancel',
        title: '',
        body: '',
    };

    Registries.Component.add(PaymentDepositPopup);

    return PaymentDepositPopup;
});
