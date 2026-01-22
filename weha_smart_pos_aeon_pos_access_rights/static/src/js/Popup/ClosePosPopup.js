odoo.define('weha_smart_pos_access_rights.ClosePosPopup', function (require) {
    'use strict';

    const ClosePosPopup = require('point_of_sale.ClosePosPopup');
    const Registries = require('point_of_sale.Registries');
    const { onMounted, useRef, useState, onWillStart } = owl;

    const AccessRightsClosePosPopup = (ClosePosPopup) => 
    class extends ClosePosPopup {
        setup() {
            super.setup();      
            this.state.is_supervisor = false;
            onWillStart(this.OnWillStart);
        }                

        OnWillStart(){
            console.log('OnWillStart');
            console.log(this.env.pos.get_cashier());
            console.log(this.env.pos.res_users_supervisor_by_id[this.env.pos.get_cashier().user_id]);
            let supervisor_id = this.env.pos.res_users_supervisor_by_id[this.env.pos.get_cashier().user_id];
            if(supervisor_id != undefined){
                this.state.is_supervisor = true;
            }
        }
    }    

    Registries.Component.extend(ClosePosPopup, AccessRightsClosePosPopup)
});
