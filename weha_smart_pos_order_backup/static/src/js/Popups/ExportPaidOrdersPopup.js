odoo.define('weha_smart_pos_base.ExportPaidOrdersPopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    const { useState } = owl;

    class ExportPaidOrdersPopup extends AbstractAwaitablePopup {

        setup() {
            super.setup();       
            this.state = useState({
                'isPaidOrdersReady': false,
                'filename': '',
                'url': '',
            });
        }
        
        async generateFile(){
            this.preparePaidOrders()
        }
        
        _createBlob(contents) {
            if (typeof contents !== 'string') {
                contents = JSON.stringify(contents, null, 2);
            }
            return new Blob([contents]);
        }
        
        preparePaidOrders() {
            try {
                this.paidOrdersBlob = this._createBlob(this.env.pos.export_paid_orders());
                this.state.isPaidOrdersReady = true;
                this.state.filename = this.paidOrdersFilename();
                this.state.url = this.paidOrdersURL();
            } catch (error) {
                console.warn(error);
            }
        }
        get paidOrdersFilename() {
            return `${this.env._t('paid orders')} ${moment().format('YYYY-MM-DD-HH-mm-ss')}.json`;
        }
        get paidOrdersURL() {
            var URL = window.URL || window.webkitURL;
            return URL.createObjectURL(this.paidOrdersBlob);
        }
    }

    ExportPaidOrdersPopup.template = 'ExportPaidOrdersPopup';
    Registries.Component.add(ExportPaidOrdersPopup);

    return ExportPaidOrdersPopup;
});

// import AbstractAwaitablePopup from 'point_of_sale.AbstractAwaitablePopup';
// import Registries from 'point_of_sale.Registries';
// // import { useState } from "@web/core/utils/hooks";

// export class ExportPaidOrdersPopup extends AbstractAwaitablePopup {
//     setup() {
//         super.setup();       
//         // this.useState = useState{
//         //     'isUnpaidOrdersReady': false,
//         // } 
//     }

//     async generateFile(){
//         this.prepareUnpaidOrders()
//     }
    
//     _createBlob(contents) {
//         if (typeof contents !== 'string') {
//             contents = JSON.stringify(contents, null, 2);
//         }
//         return new Blob([contents]);
//     }
    
//     prepareUnpaidOrders() {
//         try {
//             this.unpaidOrdersBlob = this._createBlob(this.env.pos.export_unpaid_orders());
//             this.state.isUnpaidOrdersReady = true;
//             this.state.filename = this.unpaidOrdersFilename();
//             this.state.url = this.unpaidOrdersURL();
//         } catch (error) {
//             console.warn(error);
//         }
//     }
    
//     get unpaidOrdersFilename() {
//         return `${this.env._t('unpaid orders')} ${moment().format('YYYY-MM-DD-HH-mm-ss')}.json`;    
//     }

//     get unpaidOrdersURL() {
//         var URL = window.URL || window.webkitURL;
//         return URL.createObjectURL(this.unpaidOrdersBlob);
//     }
// }

// ExportPaidOrdersPopup.template = 'ExportPaidOrdersPopup';

// Registries.Component.add(ExportPaidOrdersPopup);