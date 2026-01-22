import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";


patch(ControlButtons.prototype, {
    setup() {
        super.setup(...arguments);
        this.alert = useService("alert");
        this.notification = useService("notification");
    },

    clickOpenTopup() {
        console.log("Top-up clicked");
        this.dialog.add(NumberPopup , {
            startingValue: 0,
            title: _t("Topup"),
            getPayload: async (topupAmount) => {
                console.log("Topup Amount", topupAmount);
                if(topupAmount <= 0){
                    const ref = this.notification.add("Closable notification", { type: "success", sticky: true });
                    return;
                }               
                const order = this.pos.get_order();
                const pos_config = this.pos.config;
                const enable_deposit = this.pos.config.enable_deposit;
                const deposit_product = await pos_config.deposit_product;                
                const product = this.pos.data.models["product.product"].get(deposit_product.id);
                await this.pos.addLineToCurrentOrder({ product_id: product, price_unit:topupAmount }, {});
                order.set_is_deposit_order(true);
            }
        });       
        // this.alert.add("Top-up clicked");
    },
    clickOpenRefund() {
        console.log("Refund clicked");
        // this.alert.add("Refund clicked");
    }
    
});
