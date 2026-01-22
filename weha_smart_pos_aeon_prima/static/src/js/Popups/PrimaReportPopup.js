odoo.define('weha_smart_pos_aeon_prima.PrimaDateRangePopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');
    const { Gui } = require('point_of_sale.Gui');
    const { onMounted, useRef, useState } = owl;


    class PrimaDateRangePopup extends AbstractAwaitablePopup {
        setup() {
            super.setup();
            this.state = useState({ startDate: "", endDate: "" });
            this.startDateRef = useRef('start-date');
            this.endDateRef = useRef('end-date');
            onMounted(this.onMounted);
        }

        onMounted() {
            this.startDateRef.el.focus();
        }

        getPayload() {
            return this.state;
        }

        // confirm() {             
        //     if (this.startDate && this.endDate) {
        //         // Trigger some event or perform an action with the date range
        //         console.log(this.startDate);
        //         console.log(this.endDate);
        //     } else {
        //         Gui.showPopup('ErrorPopup', {
        //             title: 'Error',
        //             body: 'Please select both start and end dates.',
        //         });
        //     }
        // }
    }

    PrimaDateRangePopup.template = 'PrimaDateRangePopup';
    PrimaDateRangePopup.defaultProps = {
        confirmText: _lt('Ok'),
        cancelText: _lt('Cancel'),
        title: _lt('Confirm ?'),    
    };
    Registries.Component.add(PrimaDateRangePopup);

    return PrimaDateRangePopup;
});
