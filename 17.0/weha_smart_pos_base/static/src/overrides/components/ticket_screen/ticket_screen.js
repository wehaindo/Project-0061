/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";


(TicketScreen.prototype, {
    
    async onDoRefund() {

        // Override for Refund Access Rights 
        if(this.pos.config.use_store_access_rights && this.pos.config.access_rights_refund){
            const { confirmed, payload } = await this.popup.add(TextInputPopup, {
                title: _t("Supervisor PIN"),            
                placeholder: _t("Input Supervisor Pin"),
            });
            if (confirmed) {
                console.log(payload);
                console.log(this.pos.hr_employee_supervisor_by_rfid);
                var supervisor = this.pos.hr_employee_supervisor_by_rfid[payload];
                if(supervisor){
                    await super.onDoRefund();
                }else{
                    await this.popup.add(ErrorPopup, {
                        title: _t("Supervisor pin not valid!"),
                        body: _t("Please ensure your supervisor pin correct."),
                    });
                }            
            }
        }else{
            await super.onDoRefund();
        }
              
    }        
});
