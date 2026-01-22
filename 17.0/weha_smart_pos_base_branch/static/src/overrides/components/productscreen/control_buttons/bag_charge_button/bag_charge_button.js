/** @odoo-module */

import { usePos} from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { Component, useState  } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";


export class BagChargeButton extends Component {
    static template = "weha_smart_pos_base.BagChargeButton";

    setup() {
        this.pos = usePos();
        this.ui = useState(useService("ui"));
        this.popup = useService("popup");
    }

    get currentOrder() {
        return this.pos.get_order();
    }

    async onClick() {        
        // this.pos.config.is_show_product_grid = !this.pos.config.is_show_product_grid;
        console.log(this.pos.config.bag_pos_category_id)
        console.log(this.pos.config.bag_pos_category_id[0]);
        var bag_charge_products = this.pos.db.get_product_by_category(this.pos.config.bag_pos_category_id[0]);
        console.log(bag_charge_products);
        const selectionList = bag_charge_products.map((product) => ({
            id: product.id,
            label: product.display_name,
            isSelected: false,
            item: product,
        }));   

        const { confirmed, payload: selectedBagCharge } = await this.popup.add(SelectionPopup, {
            title: _t("Select the Bag Product"),
            list: selectionList,
        });

        if (confirmed) {
            console.log(selectedBagCharge);       
            this.currentOrder.add_product(selectedBagCharge, {
                quantity: 1,
            });     
        }
    }
}

ProductScreen.addControlButton({
    component: BagChargeButton,
    condition: function () {
        const { config } = this.pos;
        return config.is_show_bag_charge;
    },
});