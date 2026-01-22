odoo.define('weha_smart_pos_aeon_pms.PmsMemberButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');

    class PmsMemberButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
        async onClick() {
            const { confirmed, payload: customerInfo } = await this.showPopup('PmsMemberPopup', {'title': 'PMS Member'});
        }
    }
    PmsMemberButton.template = 'PmsMemberButton';

    ProductScreen.addControlButton({
        component: PmsMemberButton,
        condition: function() {
            return true;
        },
    });

    Registries.Component.add(PmsMemberButton);

    return PmsMemberButton;
});