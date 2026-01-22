odoo.define('weha_smart_pos_aeon_prima.ClosePosPopup', function(require){
    'use strict';
    
    const  ClosePosPopup = require('point_of_sale.ClosePosPopup');
    const Registries = require('point_of_sale.Registries');

    const PrimaSessionZReportPopup = (ClosePosPopup) => 
    class extends ClosePosPopup {
        setup() {
            super.setup();            
        }     

        async downloadPrimaZReport() {
            var self = this.env;
            var pos_session_id = self.pos.pos_session.id;
            this.env.legacyActionManager.do_action(
                'weha_smart_pos_aeon_prima.action_report_prima_session_z', {
                additional_context: {active_ids: [pos_session_id]},
            });            
        }        
    };

    Registries.Component.extend(ClosePosPopup, PrimaSessionZReportPopup)
    return ClosePosPopup;
    
});










