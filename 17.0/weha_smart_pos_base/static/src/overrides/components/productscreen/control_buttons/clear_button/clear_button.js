/** @odoo-module */

import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";


export class ClearButton extends Component {
    static template = "weha_smart_pos_base.ClearButton";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
    }

    async onClick() {
        if(this.pos.config.use_store_access_rights && this.pos.config.access_rights_clear_order){
            const { confirmed, payload } = await this.popup.add(TextInputPopup, {
                title: _t("Supervisor PIN"),            
                placeholder: _t("Input Supervisor Pin"),
            });
            if (confirmed) {                
                console.log(this.pos.hr_employee_supervisor_by_rfid);
                var supervisor = this.pos.hr_employee_supervisor_by_rfid[payload];
                if(supervisor){                                       
                    var order = this.pos.get_order();
                    var lines = order.get_orderlines();        
                    lines.filter(line => line.get_product())
                    .forEach(line => order.removeOrderline(line));                    
                }else{
                    await this.popup.add(ErrorPopup, {
                        title: _t("Supervisor pin not valid!"),
                        body: _t("Please ensure your supervisor pin correct."),
                    });
                }            
            }
        }else{
            const { confirmed } = await this.env.services.popup.add(ConfirmPopup, {
                title: _t("Clear Order"),
                body: _t(
                    "Are you sure to clear this order?"
                ),
                confirmText: _t("Yes"),
                cancelText: _t("No"),
            });
            if (confirmed) {
                console.log("Clear Order");
                var order = this.pos.get_order();
                var lines = order.get_orderlines();        
                lines.filter(line => line.get_product())
                .forEach(line => order.removeOrderline(line));
            }      
        }
    }
}

ProductScreen.addControlButton({
    component: ClearButton,
    condition: function () {
        return true;
    },
});