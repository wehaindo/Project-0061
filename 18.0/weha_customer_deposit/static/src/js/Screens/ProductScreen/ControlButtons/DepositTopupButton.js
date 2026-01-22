odoo.define('weha_customer_deposit.DepositTopupButton', function(require) {
    'use strict';

    const { parse } = require('web.field_utils');
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');

    class DepositTopupButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
      
        async onClick() {      
            console.log('click');
            let value =  0
            const { confirmed, payload } = await this.showPopup('NumberPopup', {
                title: this.env._t('Topup Amount'),
                startingValue: value,
                isInputSelected: true,
            });

            if (confirmed) {
                let product = this.env.pos.db.get_product_by_id(this.env.pos.config.deposit_product[0]);
                if(product){
                    var order = this.env.pos.get_order();                    
                    order.add_product(product, {
                        price: parse.float(payload),
                        extras: {
                            price_manually_set: true,
                        },
                    });
                    order.set_is_deposit_order(true)
                    this.showScreen('PaymentScreen');
                }             
            }
        }
    }
    DepositTopupButton.template = 'DepositTopupButton';

    ProductScreen.addControlButton({
        component: DepositTopupButton,
        condition: function() {
            return this.env.pos.get_order().get_partner() && this.env.pos.config.enable_deposit;
        },
    });

    Registries.Component.add(DepositTopupButton);

    return DepositTopupButton;
});
