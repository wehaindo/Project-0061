odoo.define('weha_smart_pos_aeon_price_change.PriceOverrideButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');

    class PriceOverrideButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }

        get get_selected_orderline() {
            return this.env.pos.get_order().get_selected_orderline();            
        }

        async onClick() {
            var orderline =  this.env.pos.get_order().get_selected_orderline();
            if (orderline) {
                const { confirmed, payload } = await this.showPopup('NumberDenomPopup', {
                    title: this.env._t('Input New Price'),
                    isInputSelected: true,
                });
                var newPrice = payload;
                if ( confirmed ) {                
                    const { confirmed, payload } = await this.showPopup('PasswordInputPopup', {
                        title: this.env._t('Supervisor Pin?'),                    
                        isInputSelected: true,                        
                    }); 

                    if ( confirmed ){
                        var supervisor = this.env.pos.res_users_supervisor_by_rfid[payload];
                        if (supervisor) {
                            console.log('supervisor');
                            console.log(supervisor);
                            orderline.price_manually_set = true;
                            orderline.set_unit_price(newPrice);
                            orderline.set_price_source('override');    
                            orderline.set_price_override_user(supervisor.id);
                        }else{
                            await this.showPopup('ErrorPopup', {
                                body: this.env._t('Price override failed!'),                    
                            });    
                        }
                    }
                }
            }
        }
    }
    
    PriceOverrideButton.template = 'PriceOverrideButton';

    ProductScreen.addControlButton({
        component: PriceOverrideButton,
        condition: function() {
            return this.env.pos.config.allow_price_override
        },
    });

    Registries.Component.add(PriceOverrideButton);

    return PriceOverrideButton;
});