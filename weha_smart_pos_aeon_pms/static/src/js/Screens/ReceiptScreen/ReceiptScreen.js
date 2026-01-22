odoo.define('weha_smart_pos_aeon_pms.ReceiptScreen', function (require) {
	'use strict';

	const ReceiptScreen = require('point_of_sale.ReceiptScreen');
	const Registries = require('point_of_sale.Registries');

    const AeonPmsReceiptScreen = (ReceiptScreen) =>
		class extends ReceiptScreen {
			setup() {
                super.setup();
                const order = this.currentOrder;
                const partner = order.get_partner();
                if (order.get_is_aeon_member()){
                    this.orderUiState.inputEmail = this.orderUiState.inputEmail || (partner && partner.email) || order.aeon_customer_email;
                }                            
            }
        }


    Registries.Component.extend(ReceiptScreen, AeonPmsReceiptScreen);
    return AeonPmsReceiptScreen;        

});