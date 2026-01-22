odoo.define('weha_smart_pos_aeon_price.SetPricelistButton', function(require) {
    'use strict';

    const SetPricelistButton = require('point_of_sale.SetPricelistButton');
    const Registries = require('point_of_sale.Registries');


    const PriceSetPricelistButton = (SetPricelistButton) =>
		class extends SetPricelistButton {
            setup() {
                super.setup();           
            }
        
            async onClick() {
            
            }
    }

    Registries.Component.extend(SetPricelistButton, PriceSetPricelistButton);

    return SetPricelistButton;
});
