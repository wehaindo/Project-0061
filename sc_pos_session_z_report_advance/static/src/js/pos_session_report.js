odoo.define('sc_pos_session_z_report_advance', function (require) {
    "use strict";

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');

    class PosCustomRepButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
        async onClick() {
            var self = this.env;
            var pos_session_id = self.pos.pos_session.id;
            this.env.legacyActionManager.do_action(
                'sc_pos_session_z_report_advance.action_report_session_z', {
                additional_context: {active_ids: [pos_session_id]},
            });
        }
    }
    PosCustomRepButton.template = 'PosCustomRepButton';

    ProductScreen.addControlButton({
        component: PosCustomRepButton,
    });

    Registries.Component.add(PosCustomRepButton);

    return PosCustomRepButton;


});
