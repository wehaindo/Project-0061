odoo.define('sc_pos_session_z_report_advance.ClosePosPopup', function(require){
    'use strict';
    
    const  ClosePosPopup = require('point_of_sale.ClosePosPopup');
    const Registries = require('point_of_sale.Registries');

    const PosSessionZReportPopup = (ClosePosPopup) => 
    class extends ClosePosPopup {
        setup() {
            super.setup();            
        }     

        async downloadZReport() {
            var self = this.env;
            var pos_session_id = self.pos.pos_session.id;
            this.env.legacyActionManager.do_action(
                'sc_pos_session_z_report_advance.action_report_session_z', {
                additional_context: {active_ids: [pos_session_id]},
            });            
        }        
    };

    Registries.Component.extend(ClosePosPopup, PosSessionZReportPopup)
    return ClosePosPopup;
    
});










