odoo.define('aspl_pos_wallet.PaymentWalletPopup', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    class PaymentWalletPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            this.state = useState({ inputchange: this.props.change});
            this.change = useRef('change');
        }
        getPayload(){
            var order = this.env.pos.get_order();
            if(order.get_client()){
                order.set_type_for_wallet('change');
                order.set_change_amount_for_wallet(order.get_change());
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
    PaymentWalletPopup.template = 'PaymentWalletPopup';

    PaymentWalletPopup.defaultProps = {
        confirmText: 'Add to Wallet',
        skipText: 'Skip',
        cancelText: 'Cancel',
        title: '',
        body: '',
    };

    Registries.Component.add(PaymentWalletPopup);

    return PaymentWalletPopup;
});
