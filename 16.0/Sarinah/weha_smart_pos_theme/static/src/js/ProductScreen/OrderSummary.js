/** @odoo-module **/

import OrderSummary from 'point_of_sale.OrderSummary';
import Registries from 'point_of_sale.Registries';

export const ShopOnOrderSummary = (OrderSummary) =>
    class ShopOnOrderSummary extends OrderSummary {
        getTotalItems() {
            var order = this.env.pos.get_order()
             var items = order.orderlines.length;
            var array = []

            for (var i = 0; i < order.orderlines.length; ++i) {
                array.push(order.orderlines[i].quantity);
            }
            var qty = array.reduce((a, b) => a + b, 0);

            return items;
        }
        getTotalQty() {
            var order = this.env.pos.get_order()
             var items = order.orderlines.length;
            var array = []

            for (var i = 0; i < order.orderlines.length; ++i) {
                array.push(order.orderlines[i].quantity);
            }
            var qty = array.reduce((a, b) => a + b, 0);

            return qty;
        }
    };

Registries.Component.extend(OrderSummary, ShopOnOrderSummary);
