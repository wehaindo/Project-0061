odoo.define('weha_smart_pos_send_message.SendMessagePopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    const { useState } = owl;

    class SendMessagePopup extends AbstractAwaitablePopup {
        setup() {
            super.setup();       
            // this.state = useState({ message: this.props.message});
        }
    }

    SendMessagePopup.template = 'SendMessagePopup';
    Registries.Component.add(SendMessagePopup);

    return SendMessagePopup;
});

