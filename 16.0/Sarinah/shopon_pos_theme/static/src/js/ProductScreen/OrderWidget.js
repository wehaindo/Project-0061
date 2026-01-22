/** @odoo-module **/

import OrderWidget from 'point_of_sale.OrderWidget';
import Registries from 'point_of_sale.Registries';

export const ShopOnOrderWidget = (OrderWidget) =>
    class ShopOnOrderWidget extends OrderWidget {
         async onClearOrder() {
            var self = this;
            if (this.env.pos.get_order() && this.env.pos.get_order().get_orderlines() && this.env.pos.get_order().get_orderlines().length > 0) {
                var orderlines = this.env.pos.get_order().get_orderlines();
                _.each(orderlines, function (each_orderline) {
                    if (self.env.pos.get_order().get_orderlines()[0]) {
                        self.env.pos.get_order().remove_orderline(self.env.pos.get_order().get_orderlines()[0]);
                    }
                });
            } else {
                alert("No any product in cart");
            }
        }
    };

Registries.Component.extend(OrderWidget, ShopOnOrderWidget);
