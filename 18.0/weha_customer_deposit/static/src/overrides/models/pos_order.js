import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";


patch(PosOrder.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);        
        this.is_deposit_order = false;                
    },

    is_deposit_order() {
        return this.is_deposit_order;
    },

    set_is_deposit_order(is_deposit_order) {
        console.log("Setting deposit order:", is_deposit_order);
        this.is_deposit_order = is_deposit_order;
    }

});