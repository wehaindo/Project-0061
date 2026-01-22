odoo.define('weha_smart_pos_base.ExportUnpaidOrdersButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');
    const { ConnectionLostError, ConnectionAbortedError } = require('@web/core/network/rpc_service')
    const { identifyError } = require('point_of_sale.utils');

    class ExportUnpaidOrdersButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
        async onClick() {
            this.showPopup('ExportUnpaidOrdersPopup');
        }
    }
    ExportUnpaidOrdersButton.template = 'ExportUnpaidOrdersButton';

    ProductScreen.addControlButton({
        component: ExportUnpaidOrdersButton,
        condition: function() {
            return this.env.pos.config.is_allow_export_unpaid_order;
        }
    });

    Registries.Component.add(ExportUnpaidOrdersButton);

    return ExportUnpaidOrdersButton;
});