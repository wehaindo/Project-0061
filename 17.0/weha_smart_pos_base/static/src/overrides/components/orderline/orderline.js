/** @odoo-module */

import { Orderline  } from "@point_of_sale/app/generic_components/orderline/orderline";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";


import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";



patch(Orderline.prototype, {
    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
    },

    async onPlusButtonClicked() {
        const order = this.pos.get_order();
        const selectedLine = order.get_selected_orderline();        
        var line_qty = selectedLine.quantity 
        selectedLine.set_quantity(line_qty + 1);
    },
    
    async onMinusButtonClicked(){
        const order = this.pos.get_order();
        const selectedLine = order.get_selected_orderline();        
        var line_qty = selectedLine.quantity 
        selectedLine.set_quantity(line_qty - 1);
    },

    async onDeleteButtonClicked(){
        if(this.pos.config.use_store_access_rights && this.pos.config.access_rights_del_orderline){
            const { confirmed, payload } = await this.popup.add(TextInputPopup, {
                title: _t("Supervisor PIN"),            
                placeholder: _t("Input Supervisor Pin"),
            });
            if (confirmed) {                
                console.log(this.pos.hr_employee_supervisor_by_rfid);
                var supervisor = this.pos.hr_employee_supervisor_by_rfid[payload];
                if(supervisor){                                       
                    var order = this.pos.get_order();
                    var orderline = order.get_selected_orderline();
                    order.removeOrderline(orderline);              
                }else{
                    await this.popup.add(ErrorPopup, {
                        title: _t("Supervisor pin not valid!"),
                        body: _t("Please ensure your supervisor pin correct."),
                    });
                }            
            }
        }else{
            var order = this.pos.get_order();
            var orderline = order.get_selected_orderline();
            const { confirmed } = await this.env.services.popup.add(ConfirmPopup, {
                title: _t("Remove Item"),
                body: _t(
                    "Are you sure to remove " + orderline.full_product_name + " ?"
                ),
                confirmText: _t("Yes"),
                cancelText: _t("No"),
            });
            if (confirmed) {               
                order.removeOrderline(orderline);
            }      
        }
       
    }

});