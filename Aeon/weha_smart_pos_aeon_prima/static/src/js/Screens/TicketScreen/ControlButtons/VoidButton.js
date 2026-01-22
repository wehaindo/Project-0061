odoo.define('weha_smart_pos_aeon_prima.VoidButton', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const VoidButton = require('weha_smart_pos_disable_refund.VoidButton');
    const Registries = require('point_of_sale.Registries');

    const PrimaVoidButton = (VoidButton) =>
        class extends VoidButton {
    
            setup() {
                super.setup();            
            }
        
            async add_payments(order, void_order){
                console.log('weha_smart_pos_disable_refund.VoidButton.add_payment');                  
                order.get_paymentlines().forEach(function(paymentLine){
                    console.log(paymentLine);
                    var payment = void_order.add_paymentline(paymentLine.payment_method);                
                    payment.set_partner_reference_no(paymentLine.get_partner_reference_no());
                    payment.set_reference_no(paymentLine.get_reference_no());
                    payment.set_external_id(paymentLine.get_external_id());
                });                
            }
        }

    Registries.Component.extend(VoidButton, PrimaVoidButton);
});