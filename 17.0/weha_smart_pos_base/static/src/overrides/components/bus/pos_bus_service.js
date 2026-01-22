/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosBus } from "@point_of_sale/app/bus/pos_bus_service";
import { _t } from "@web/core/l10n/translation";
import { InfoPopup } from "@weha_smart_pos_base/app/utils/info_popup/info_popup";

patch(PosBus.prototype, {
    
    setup() {
        super.setup(...arguments);    
    },

    // Override
    dispatch(message) {
        super.dispatch(...arguments);

        if(message.type === 'notification'){              
            console.log(message);            
            const config  = this.pos.config;
            console.log(config);
            var curChannel = "pos_session-" + config.current_session_id[0].toString() + "-" + this.pos.pos_session.access_token;                        
            console.log(curChannel)
            if(message.payload.channel === curChannel){                
                console.log(curChannel + ' is match');
                this.pos.popup.add(InfoPopup, {
                    title: _t("Message from Server"),
                    body: _t(message.payload.data),
                });
                // this.pos_notification.add(_t("The order has been already paid."), 3000);
                // this.notification.add(_t("Broadcast Message"),
                // {
                //     title: _t("warning head"),
                //     type: "warning",	
                //     sticky: true                
                // });
            }
        }
    },
});

PosBus.serviceDependencies = ["pos", "orm", "bus_service", "pos_notification"];