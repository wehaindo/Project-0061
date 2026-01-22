odoo.define('weha_smart_pos_aeon_promotion.PromoQuantityButton', function(require) {
    'use strict';

    const { parse } = require('web.field_utils');
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');

    class PromoQuantityButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }

        async onClick() {
            var order = this.env.pos.get_order();
            var orderline = order.get_selected_orderline();
            if (orderline.get_price_source() === 'mix_and_match'){
                const { confirmed, payload } = await this.showPopup('NumberPopup', {
                    title: this.env._t('Set Quantity'),
                    startingValue: orderline.get_quantity(),
                    isInputSelected: true,
                });
    
                if (confirmed) {                
                    console.log(parse.float(payload));
                    orderline.set_quantity(parse.float(payload));
                }
            }
        }
    }

    PromoQuantityButton.template = 'PromoQuantityButton';

    ProductScreen.addControlButton({
        component: PromoQuantityButton,
        condition: function() {
            return true;
        },
    });

    Registries.Component.add(PromoQuantityButton);

    return PromoQuantityButton;
});
