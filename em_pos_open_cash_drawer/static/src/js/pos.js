odoo.define('em_pos_open_cash_drawer', function (require) {
"use strict";

    const { useListener } = require("@web/core/utils/hooks");
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const PosActivityLog = require('weha_smart_pos_aeon_activity_log.PosActivityLog');

    const PosResProductScreen = (ProductScreen) =>
        class extends ProductScreen {
        setup() {
            super.setup();
            this.posActivityLog = new PosActivityLog();
            useListener('click-open-cashbox', this._openCashDrawer);

        }
        
        getFormattedDateTime() {
            const now = new Date();

            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0'); // Months are zero-based
            const day = String(now.getDate()).padStart(2, '0');
        
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
        
            return `${day}-${month}-${year} ${hours}:${minutes}:${seconds}`;
        } 

        async _openCashDrawer() {         	
            var order = this.env.pos.get_order();
            const {payload} = await this.showPopup('TextInputPopup', {
                title: 'Confirmation',
                body: `[${this.env.pos.get_cashier().name} on ${this.getFormattedDateTime()}] want to open cash drawer ? Please input reason`,
                confirmText: 'Okay',
                cancelText: 'Cancel',
            });
            if(payload){
                // name, details, hr_employee_id, pos_config_id, pos_session_id, pos_order_reference
                // this.posActivityLog.saveLogToLocalStorage('Product Screen','Clear Order All - ' + payload, order.cashier.id, this.env.pos.config.id, 
                // this.env.pos.session.id);
                console.log(this.pos);
                this.posActivityLog.saveLogToLocalStorage(
                    'Product Screen',
                    'Open Cash Drawer - ' + payload,
                    this.env.pos.user.id,
                    order.cashier.id,
                    this.env.pos.config.id,
                    this.env.pos.pos_session.id,
                    false
                );
                $("<center><div id='content_id'>Open Cash Drawer</div></center>").print();
            }
        }
    }

    Registries.Component.extend(ProductScreen, PosResProductScreen);

    const PaymentScreen2 = (PaymentScreen) =>
    class extends PaymentScreen {
        setup() {
            super.setup();
            this.posActivityLog = new PosActivityLog();
        }
        new_js_cashdrawer() {
            var self = this;
            var order = this.env.pos.get_order();
            this.posActivityLog.saveLogToLocalStorage('Product Screen','Open Cash Drawer',order.cashier.id);
            $("<center><div id='content_id'>Open Cash Drawer</div></center>").print();
        }
    }
    Registries.Component.extend(PaymentScreen, PaymentScreen2);
});

