odoo.define('pos_cash_opening_zero.HeaderLockButton', function(require) {
    'use strict';

    const HeaderLockButton = require('point_of_sale.HeaderLockButton');
    const Registries = require("point_of_sale.Registries");
    const PosActivityLog = require('weha_smart_pos_aeon_activity_log.PosActivityLog');

    const PosCashOpeningZeroHeaderLockButton = (HeaderLockButton) =>    
        class extends HeaderLockButton {
            setup() {
                super.setup();
                this.posActivityLog = new PosActivityLog();
            }
            
            getCurrentOrdersCount() {
                if (this.env.pos) {
                    return this.env.pos.get_order_list().length;
                } else {
                    return 0;
                }
            }

            async showLoginScreen() {
                const currentOrdersCount = this.getCurrentOrdersCount();
                if (currentOrdersCount > 1) {   
                    await this.showPopup('ErrorPopup', {    
                        title: this.env._t('Cannot Lock POS'),
                        body: this.env._t('Please complete or discard all current orders before locking the POS.'),     
                    });
                    return;
                }
                const order = this.env.pos.get_order();
                if (order && !order.is_empty()) {
                    await this.showPopup('ErrorPopup', {    
                        title: this.env._t('Cannot Lock POS'),
                        body: this.env._t('Please complete or discard the current order before locking the POS.'),     
                    });
                    return;
                }   
                this.env.pos.reset_cashier();
                await this.showTempScreen('LoginScreen');
            }
        }
    
    Registries.Component.extend(HeaderLockButton, PosCashOpeningZeroHeaderLockButton);
});