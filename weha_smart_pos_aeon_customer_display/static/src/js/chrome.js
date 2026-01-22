odoo.define('weha_smart_pos_aeon_customer_display.Chrome', function(require){
    'use strict'

    const Chrome = require('point_of_sale.Chrome');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");

    const PosCustomerDisplayChrome = (Chrome) =>
    class extends Chrome {
        /**
         * @override
         */
        setup(){
            super.setup();
        }

    }

    Registries.Component.extend(Chrome, PosCustomerDisplayChrome);

    return Chrome;
});