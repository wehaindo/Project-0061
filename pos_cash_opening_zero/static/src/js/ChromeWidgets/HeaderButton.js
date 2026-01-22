odoo.define('pos_cash_opening_zero.HeaderButton', function(require) {
    'use strict';

    const HeaderButton = require('point_of_sale.HeaderButton');
    const Registries = require("point_of_sale.Registries");
    const PosActivityLog = require('weha_smart_pos_aeon_activity_log.PosActivityLog');

    const PosCashOpeningZeroHeaderButton = (HeaderButton) => 
        class extends HeaderButton {
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

            async onClick() {
                try {
                    const currentOrdersCount = this.getCurrentOrdersCount();
                    if (currentOrdersCount > 1) {   
                        await this.showPopup('ErrorPopup', {
                            title: this.env._t('Cannot Close POS'),
                            body: this.env._t('Please complete or discard all current orders before closing the POS.'),     
                        });
                        return;
                    }
                    const order = this.env.pos.get_order();
                    if (order && !order.is_empty()) {
                        await this.showPopup('ErrorPopup', {
                            title: this.env._t('Cannot Close POS'),
                            body: this.env._t('Please complete or discard the current order before closing the POS.'),     
                        });
                        return;
                    }
                    const info = await this.env.pos.getClosePosInfo();
                    this.showPopup('ClosePosPopup', { info: info, keepBehind: true });
                } catch (e) {
                    if (isConnectionError(e)) {
                        this.showPopup('OfflineErrorPopup', {
                            title: this.env._t('Network Error'),
                            body: this.env._t('Please check your internet connection and try again.'),
                        });
                    } else {
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Unknown Error'),
                            body: this.env._t('An unknown error prevents us from getting closing information.'),
                        });
                    }
                }
            }

        }
    
    Registries.Component.extend(HeaderButton, PosCashOpeningZeroHeaderButton);
    return PosCashOpeningZeroHeaderButton;
});