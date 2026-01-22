odoo.define('weha_smart_pos_access_rights.FingerprintAuthPopup', function (require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { onMounted, useRef, useState } = owl;


    class FingerprintAuthPopup extends AbstractAwaitablePopup {
        setup(){
            super.setup();
        }

        async confirm(){            
            super.confirm();                
        }

        async handleClosingError(message) {
            await this.showPopup('ErrorPopup', {title: 'Error', body: message});
        }
    }

    FingerprintAuthPopup.template = 'FingerprintAuthPopup';

    Registries.Component.add(FingerprintAuthPopup);

    return FingerprintAuthPopup;

});