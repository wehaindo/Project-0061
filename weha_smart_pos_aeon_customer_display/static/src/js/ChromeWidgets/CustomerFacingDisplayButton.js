odoo.define('weha_smart_pos_aeon_customer_display.CustomerFacingDisplayButton', function(require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const CustomerFacingDisplayButton  = require('point_of_sale.CustomerFacingDisplayButton');

    const { useState } = owl;

    var AeonCustomerFacingDisplayButton = CustomerFacingDisplayButton => class extends CustomerFacingDisplayButton {     
        setup() {
            super.setup();         
        }
    }

    Registries.Component.extend(CustomerFacingDisplayButton, AeonCustomerFacingDisplayButton);

});