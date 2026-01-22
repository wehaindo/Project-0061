odoo.define('weha_smart_pos_aeon_prima.PrimaWaitingPopup', function(require) {
    'use strict';
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');


    class PrimaWaitingPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
        }

        get currentOrder() {
            return this.env.pos.get_order();
        }
    }

        //Create products popup
    PrimaWaitingPopup.template = 'PrimaWaitingPopup';
    PrimaWaitingPopup.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: 'Prima - Waiting Payment Status',
        body: '',
        primaPaymentStatus: 'Processing...',
        invoiceUrl: '',
        qrCodeImage: ''
    };
    Registries.Component.add(PrimaWaitingPopup);
    return PrimaWaitingPopup;
})