odoo.define('weha_smart_pos_aeon_prima.PrimaSessionReport', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");


    class PrimaSessionReport extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
        async onClick() {            
            var self = this.env;
            var pos_session_id = self.pos.pos_session.id;
            this.env.legacyActionManager.do_action(
                'weha_smart_pos_aeon_prima.action_report_prima_session_z', {
                additional_context: {active_ids: [pos_session_id]},
            });            
        }
    }
    PrimaSessionReport.template = 'PrimaSessionReport';

    ProductScreen.addControlButton({
        component: PrimaSessionReport,
        condition: function() {
            return this.env.pos.config.enable_prima_session_report;
        },
    });

    Registries.Component.add(PrimaSessionReport);

    return PrimaSessionReport;
});
