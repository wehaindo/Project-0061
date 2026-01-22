odoo.define('weha_smart_pos_aeon_price_change.PriceOverrideButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');

    class PriceOverrideButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }

        get get_selected_orderline() {
            return this.env.pos.get_order().get_selected_orderline();
        }

        async onClick() {
            var orderline =  this.env.pos.get_order().get_selected_orderline();
            
        }
    }
    PriceOverrideButton.template = 'PriceOverrideButton';

    ProductScreen.addControlButton({
        component: PriceOverrideButton,
        condition: function() {
            return this.env.pos.config.is_show_bag_charge
        },
    });

    Registries.Component.add(PriceOverrideButton);

    return PriceOverrideButton;
});