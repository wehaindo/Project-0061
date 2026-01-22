odoo.define('weha_smart_pos_voucher.giftVoucherControlButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');

    class giftVoucherControlButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
        async onClick() {
            this.showScreen('GiftVoucherScreen');
        }
    }

    giftVoucherControlButton.template = 'giftVoucherControlButton';

    ProductScreen.addControlButton({
        component: giftVoucherControlButton,
        condition: function() {
            return this.env.pos.config.enable_gift_voucher;
        },

    });
    Registries.Component.add(giftVoucherControlButton);

    return giftVoucherControlButton;
});
