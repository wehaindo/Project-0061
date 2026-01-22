odoo.define('weha_smart_pos_aeon_pos_order_log.ReceiptScreen', function(require) {
    'use strict';
        
    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');
    const PosOrderReceiptLog = require('weha_smart_pos_aeon_pos_order_log.PosOrderReceiptLog');
    const { Printer } = require('point_of_sale.Printer');

    const PosOrderLogReceiptScreen = (ReceiptScreen) =>
        class extends ReceiptScreen {

            setup() {
                super.setup();
                this.posOrderReceiptLog = new PosOrderReceiptLog();
            }

            async printReceipt() {
                const printer = new Printer(null, this.env.pos);                
                const receiptString = this.orderReceipt.el.innerHTML;
                console.log(this.orderReceipt.el.innerHTML);                
                const ticketImage = await printer.htmlToImg(receiptString);                
                const order_data = this.currentOrder;
                this.posOrderReceiptLog.saveLogToLocalStorage(false, order_data['pos_session_id'], order_data['name'],  receiptString, ticketImage)                
                super.printReceipt();
            }
            
        } 

    Registries.Component.extend(ReceiptScreen, PosOrderLogReceiptScreen);
    return ReceiptScreen;
})

