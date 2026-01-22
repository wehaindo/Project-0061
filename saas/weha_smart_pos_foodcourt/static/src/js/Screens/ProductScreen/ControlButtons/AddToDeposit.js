odoo.define('weha_smart_pos_foodcourt.AddToDeposit', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class AddToDepositButton extends PosComponent {
        constructor(){
            super(...arguments);
        }
        orderIsEmpty(order){
            var self = this;
            if(!order.is_empty()){
                let lines_ids = _.pluck(order.get_orderlines(), 'id');
                _.each(lines_ids,function(id){
                    order.remove_orderline(order.get_orderline(id));
                });
            }
        }
        async onClick(){
            let order =  this.env.pos.get_order();
            const { confirmed, payload: rechargeAmount } = await this.showPopup('TopupDepositPopup', {
                customer: order.get_client().name || false,
                rechargeAmount:'',
                title: this.env._t('Add Money'),
            });
            if (confirmed){
                if(this.env.pos.get_order().get_orderlines().length > 0){
                    const { confirmed } = await this.showPopup('ConfirmPopup', {
                        title: this.env._t('would you like to discard this order?'),
                        body: this.env._t(
                            'If you want to recharge wallet then you have to discard this order'
                        ),
                    });
                    if (confirmed) {
//                        order.destroy()
                        this.orderIsEmpty(order);
                    }
                }
                let product = this.env.pos.db.get_product_by_id(this.env.pos.config.deposit_product[0]);
                if(product){
                    order.add_product(product, {
                        price: Number(rechargeAmount),
                        extras: {
                            price_manually_set: true,
                        },
                    });
                    order.set_client(order.get_client())
                    order.set_type_for_deposit('recharge')
                    this.showScreen('PaymentScreen');
                }
            }
        }
    }

    AddToDepositButton.template = 'AddToDepositButton';

    ProductScreen.addControlButton({
        component: AddToDepositButton,
        condition: function(){
            return this.env.pos.config.enable_deposit && this.env.pos.get_client();
        },
    });

    Registries.Component.add(AddToDepositButton);
    return AddToDepositButton;
});
