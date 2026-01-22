odoo.define('weha_smart_pos_aeon_pms.VoidButton', function (require) {
    'use strict';

    const { useListener } = require("@web/core/utils/hooks");
    const { isConnectionError } = require('point_of_sale.utils');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const VoidButton = require('weha_smart_pos_disable_refund.VoidButton');

    const PmsVoidButton = (VoidButton) =>
    class extends VoidButton {

        init_data(order, void_order){
            super.init_data(order, void_order);
            if(order.get_is_aeon_member()){
                void_order.set_aeon_member(order.get_aeon_member());
                void_order.set_aeon_member_day(order.get_aeon_member_day());
                void_order.set_card_no(order.get_card_no());
            }
            console.log('void_order');
            console.log(void_order);
        }
    
        add_payments(order, void_order){
            console.log('weha_smart_pos_aeon_pms.VoidButton.add_payment');
            super.add_payments(order, void_order);
            console.log(order.payentlines);
            for (const payment of order.paymentlines) {          
                void_order.add_paymentline(payment.payment_method.id);
                void_order.selected_paymentline.set_amount(payment.amount);
            }
        }

    }
    
    Registries.Component.extend(VoidButton, PmsVoidButton);
    return VoidButton;

});