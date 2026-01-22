odoo.define('weha_smart_pos_aeon_pos_order_log.PaymentScreen', function(require) {
    'use strict';
    
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const PosOrderLog = require('weha_smart_pos_aeon_pos_order_log.PosOrderLog');

    const PosOrderLogPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {

            setup() {
                super.setup();
                this.posOrderLog = new PosOrderLog();
            }

            async _finalizeValidation() {
                const order_data = this.currentOrder;
                this.posOrderLog.saveLogToLocalStorage(false, order_data['pos_session_id'], order_data['name'],  order_data.export_as_JSON())                
                super._finalizeValidation();
            }                       
        } 

    Registries.Component.extend(PaymentScreen, PosOrderLogPaymentScreen);
    return PaymentScreen;
})

