/** @odoo-module */

import { Component } from "@odoo/owl";
import { parseFloat } from "@web/views/fields/parsers";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";


export class TopupButton extends Component {
    static template = "weha_smart_pos_base.TopupButton";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
    }

    async onClick() {
        let value =  0
        const { confirmed, payload: topupAmount } = await this.popup.add(NumberPopup, {
            title: _t("Topup Amount"),
            startingValue: value,
            isInputSelected: true,             
        });
        if (confirmed) {                
            console.log(topupAmount);
            let product = this.pos.db.get_product_by_id(this.pos.config.deposit_product[0]);
            if(product){
                var order = this.pos.get_order();                    
                order.add_product(product, {
                    price: parseFloat(topupAmount),
                    extras: {
                        price_manually_set: true,
                    },
                });
                order.set_is_deposit_order(true);
                this.pos.showScreen('PaymentScreen');
            }else{

            }     
        }
    }
}

ProductScreen.addControlButton({
    component: TopupButton,
    condition: function () {
        const { config } = this.pos;
        return config.enable_deposit && this.pos.get_order().get_partner();
    },
});