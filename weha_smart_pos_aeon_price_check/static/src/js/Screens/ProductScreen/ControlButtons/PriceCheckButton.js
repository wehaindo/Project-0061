odoo.define('weha_smart_pos_aeon_price_check.PriceCheckButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');

    class PriceCheckButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }

        async onClick() {
            const { confirmed, payload } = await this.showPopup('TextInputPopup', {
                title: this.env._t('Scan Product Barcode'),                    
                isInputSelected: true,
                placeholder:'Product Barcode'
            }); 

            if (confirmed){
                var product = this.env.pos.db.get_product_by_barcode(payload);
                if ( product ){
                    const { confirmed } = await this.showPopup('ConfirmPopup', {
                        title: this.env._t('Price Information'),
                        body: product.display_name + " : " + product.lst_price,
                    });
                }else{
                    await this.showPopup('ErrorPopup', {
                        body: this.env._t('Product or Item not found!'),                    
                    });  
                }
            }else{
                return;
            }
        }
    }
    PriceCheckButton.template = 'PriceCheckButton';

    ProductScreen.addControlButton({
        component: PriceCheckButton,
        condition: function() {
            return this.env.pos.config.is_show_price_check
        },
    });

    Registries.Component.add(PriceCheckButton);

    return PriceCheckButton;
});