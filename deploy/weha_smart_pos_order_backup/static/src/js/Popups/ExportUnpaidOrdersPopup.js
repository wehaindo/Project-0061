odoo.define('weha_smart_pos_base.ExportUnpaidOrdersPopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    const { useState } = owl;

    class ExportUnpaidOrdersPopup extends AbstractAwaitablePopup {

        setup() {
            super.setup();       
            this.state = useState({
                'isUnpaidOrdersReady': false,
                'filename': '',
                'url': '',
            });
        }
        
        async generateFile(){
            this.prepareUnpaidOrders()
        }
        
        _createBlob(contents) {
            if (typeof contents !== 'string') {
                contents = JSON.stringify(contents, null, 2);
            }
            return new Blob([contents]);
        }
        
        prepareUnpaidOrders() {
            try {
                this.unpaidOrdersBlob = this._createBlob(this.env.pos.export_unpaid_orders());
                this.state.isUnpaidOrdersReady = true;
                this.state.filename = this.unpaidOrdersFilename();
                this.state.url = this.unpaidOrdersURL();
            } catch (error) {
                console.warn(error);
            }
        }
        
        unpaidOrdersFilename() {
            return `${this.env._t('unpaid orders')} ${moment().format('YYYY-MM-DD-HH-mm-ss')}.json`;    
        }
    
        unpaidOrdersURL() {
            var URL = window.URL || window.webkitURL;
            return URL.createObjectURL(this.unpaidOrdersBlob);
        }
    }

    ExportUnpaidOrdersPopup.template = 'ExportUnpaidOrdersPopup';
    Registries.Component.add(ExportUnpaidOrdersPopup);

    return ExportUnpaidOrdersPopup;
});