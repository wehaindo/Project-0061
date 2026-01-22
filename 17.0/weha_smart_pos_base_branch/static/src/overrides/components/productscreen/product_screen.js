/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";

patch(ProductScreen.prototype, {
    setup() {
        super.setup();
        this.posbus = useService('pos_bus');    
        var order = this.pos.get_order();
        // Default Customer
        if (!order.get_partner()) {
            if (this.pos.config.is_set_default_customer && this.pos.config.customer_id) {
                var customer_id = this.pos.db.get_partner_by_id(this.pos.config.customer_id[0]);
                if (customer_id) {
                    order.set_partner(customer_id);
                }
            } else if (this.pos && this.pos.get_order()) {
                this.pos.get_order().set_partner(null);
            }
        }        
    },
    get totalItems() {
        var order = this.pos.get_order();
        var orderlines = order.orderlines;
        return orderlines.length;
    },
    get totalQuantity(){        
        var order = this.pos.get_order();
        var orderlines = order.orderlines;
        var quantity = 0;
        orderlines.forEach(orderline => {
            quantity = quantity + orderline.get_quantity();
        });
        return quantity;        
    }

});
