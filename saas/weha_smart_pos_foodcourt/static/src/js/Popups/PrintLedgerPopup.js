odoo.define('weha_smart_pos_foodcourt.PrintLedgerPopup', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    class PrintLedgerPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            this.state = useState({ startDate: false, endDate: moment().format('YYYY-MM-DD') });
            this.inputRef = useRef('input');
        }
        async confirm(){
            if(!this.state.startDate || !this.state.endDate) return
            if(moment(this.state.startDate) > moment(this.state.endDate)) return
            this.props.resolve({ confirmed: true, payload: await this.getPayload() });
            this.trigger('close-popup');
        }
        getPayload(){
            return this.state;
        }
    }
    PrintLedgerPopup.template = 'PrintLedgerPopup';
    PrintLedgerPopup.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: '',
        body: '',
    };

    Registries.Component.add(PrintLedgerPopup);

    return PrintLedgerPopup;
});
