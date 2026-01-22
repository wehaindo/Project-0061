odoo.define('bi_pos_combo.PartnerScreenExtend', function(require) {
	"use strict";

	const Registries = require('point_of_sale.Registries');
	const PartnerScreen = require('point_of_sale.PartnerListScreen'); 
	const NumberBuffer = require('point_of_sale.NumberBuffer');
	const { Gui } = require('point_of_sale.Gui');
	const { useListener } = require("@web/core/utils/hooks");


	const BiPartnerScreen = (PartnerScreen) =>
		class extends PartnerScreen {
			setup() {
				super.setup();
			}
			async clickPartner(partner) {

	            var orderlines = this.env.pos.get_order() ? this.env.pos.get_order().get_orderlines() : [];
	            const{Confirmed} = false;
	            if(this.env.pos.config.combo_pack_price== 'all_product' && orderlines.length > 0){
	                for (var line in orderlines)
	                {
	                    if(orderlines[line] && orderlines[line].product && orderlines[line].product.is_pack){
	                        const { confirmed } = await Gui.showPopup('ConfirmPopup', {
	                            title: this.env._t('Warning'),
	                            body: this.env._t('If you change customer then the price of the combo product will be changed.'),
	                        });
	                        if(confirmed){
	                        	if (this.state.selectedPartner && this.state.selectedPartner.id === partner.id) {
					                this.state.selectedPartner = null;
					            } else {
					                this.state.selectedPartner = partner;
					            }
					            this.confirm();
					            
				            }
					        else{
					        	this.trigger('close-temp-screen');
					        	return
					        }

	                    }
	                }
	                
	            }
	           	if (this.state.selectedPartner && this.state.selectedPartner.id === partner.id) {
	                this.state.selectedPartner = null;
	            } else {
	                this.state.selectedPartner = partner;
	            }
	            this.confirm();
	        }
		};

	Registries.Component.extend(PartnerScreen, BiPartnerScreen);

	return PartnerScreen;

});