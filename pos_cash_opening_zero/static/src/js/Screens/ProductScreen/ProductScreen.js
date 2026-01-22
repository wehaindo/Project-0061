odoo.define('pos_cash_opening_zero.ProductScreen', function (require) {
    'use strict';

    const { useState, useRef, onMounted, onWillStart} = owl;
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');

    const PosCashOpeningZeroProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            setup() {
                super.setup();             
            }           

            async _clickProduct(event) {
                // Show popup instead of adding product
                let supervisor_id = this.env.pos.res_users_supervisor_by_id[this.env.pos.get_cashier().user_id];                
                if (supervisor_id != undefined){
                    await this.showPopup('ErrorPopup', {
                        title: this.env._t('Adding Products Disabled'),
                        body: this.env._t('Adding products to order is currently disabled.'),
                    });
                    return;
                }
                return super._clickProduct(event);
            }

            async _barcodeProductAction(code) {
                // Disable barcode scanning as well
                let supervisor_id = this.env.pos.res_users_supervisor_by_id[this.env.pos.get_cashier().user_id];                
                if (supervisor_id != undefined){
                    await this.showPopup('ErrorPopup', {
                        title: this.env._t('Adding Products Disabled'),
                        body: this.env._t('Adding products via barcode is currently disabled.'),
                    });
                    return;
                }
                return super._barcodeProductAction(code);
            }
        };

    Registries.Component.extend(ProductScreen, PosCashOpeningZeroProductScreen);

    return PosCashOpeningZeroProductScreen;
});