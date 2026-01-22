odoo.define('point_of_sale.ImportOrdersPopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');
    const { getFileAsText } = require('point_of_sale.utils');


    const { onMounted, useRef, useState } = owl;

    class ImportOrdersPopup extends AbstractAwaitablePopup {
        setup() {
            super.setup();
            this.fileRef = useRef('fileImport');
            onMounted(this.onMounted);
        }
        
        onMounted() {
            this.fileRef.el.focus();
        }

        async importOrders(event){
            const file = event.target.files[0];
            if (file) {
                const report = this.env.pos.import_orders(await getFileAsText(file));
                await this.showPopup('OrderImportPopup', { report });
            }
        }

        // getPayload() {
        //     return this.state.inputValue;
        // }
    }
    ImportOrdersPopup.template = 'ImportOrdersPopup';
    Registries.Component.add(ImportOrdersPopup);

    return ImportOrdersPopup;
});