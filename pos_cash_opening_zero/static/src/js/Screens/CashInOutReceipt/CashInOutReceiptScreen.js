odoo.define('pos_cash_opening_zero.CashInOutReceiptScreen', function (require) {
    'use strict';

    const { Printer } = require('point_of_sale.Printer');
    const { useErrorHandlers } = require('point_of_sale.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const AbstractReceiptScreen = require('point_of_sale.AbstractReceiptScreen');
    const { useAsyncLockedMethod } = require('point_of_sale.custom_hooks');

    const { onMounted, useRef, status } = owl;

    const CashInOutReceiptScreen = (AbstractReceiptScreen) => {
        class CashInOutReceiptScreen extends AbstractReceiptScreen {
            setup() {
                super.setup();
                useErrorHandlers();
                this.cashInOutReceipt = useRef('cashinout-receipt');
                console.log(this.props);
                this.data = this.props.data;
            }
     
            confirm() {
                this.showScreen('ProductScreen', { reuseSavedUIState: true });
            }
            
            async printReceipt(){
                console.log('Print Receipt');
                const isPrinted = await this._printReceipt();
            }

            get receiptData(){
                return this.data;
            }
            
        }   
        CashInOutReceiptScreen.template = 'CashInOutReceiptScreen';
        return CashInOutReceiptScreen;
            
    }
    
    Registries.Component.addByExtending(CashInOutReceiptScreen, AbstractReceiptScreen);
    return CashInOutReceiptScreen;
});