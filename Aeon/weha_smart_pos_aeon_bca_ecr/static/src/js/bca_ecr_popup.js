odoo.define('weha_smart_pos_aeon_bca_ecr.BcaEcrPopup', function(require) {
    'use strict';
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const PosComponent = require('point_of_sale.PosComponent');
    const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    // const { useListener } = require('web.custom_hooks');
    // const { useState } = owl.hooks;
    
    class BcaEcrPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
        }

        get currentOrder() {
            return this.env.pos.get_order();
        }
    }

        //Create products popup
    BcaEcrPopup.template = 'BcaEcrPopup';
    BcaEcrPopup.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: 'BCA ECR',
        body: '',
        xenditPaymentStatus: 'Processing...',
        invoiceUrl: '',
        qrCodeImage: ''
    };
    Registries.Component.add(BcaEcrPopup);
    return BcaEcrPopup;
})