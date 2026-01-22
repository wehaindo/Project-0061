odoo.define('weha_customer_deposit.OrderReceipt', function(require) {
    'use strict';

    const OrderReceipt = require('point_of_sale.OrderReceipt');
    const Registries = require('point_of_sale.Registries');

    const { onWillUpdateProps } = owl;

    const DepositOrderReceipt = (OrderReceipt) =>
    class extends OrderReceipt {
        setup() {
            super.setup();
            this.order = this.env.pos.get_order();
        }

        get_is_deposit_order(){
            return this.order.get_is_deposit_order();            
        }

        get_remaining_deposit_amount() {
            return this.order.get_partner().remaining_deposit_amount;
        }
    }

    Registries.Component.extend(OrderReceipt, DepositOrderReceipt);

    return OrderReceipt;
});