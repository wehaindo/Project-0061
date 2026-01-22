odoo.define('weha_smart_pos_foodcourt.ClientListScreen', function(require) {

    const ClientListScreen = require('point_of_sale.ClientListScreen');
    const Registries = require('point_of_sale.Registries');
    const session = require('web.session');
    const { useState } = owl.hooks;
    const { useListener } = require('web.custom_hooks');

    const DepositClientListScreen = ClientListScreen =>
        class extends ClientListScreen {
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
            async addMoneyToWallet(){
                const { confirmed, payload: rechargeAmount } = await this.showPopup('TopupDepositPopup', {
                    customer: this.state.selectedClient.name || false,
                    rechargeAmount:'',
                    title: this.env._t('Add Money'),
                });
                if (confirmed) {
                    let order =  this.env.pos.get_order();
                    let product = this.env.pos.db.get_product_by_id(this.env.pos.config.wallet_product[0]);
                    if(product){
                        //REMOVE ORDERLINES FROM THE CART
                        this.orderIsEmpty(order);
                        //ADD PRODUCT TO CART WITH PRICE UPDATE
                        order.add_product(product, {
                            price: Number(rechargeAmount),
                            lst_price: Number(rechargeAmount),
                            extras: {
                                price_manually_set: true,
                            },
                        });
                        order.set_client(this.state.selectedClient);
                        this.back();
                        order.set_type_for_deposit('recharge');
                        this.showScreen('PaymentScreen');
                    }
                }
            }
        };

    Registries.Component.extend(ClientListScreen, DepositClientListScreen);

    return ClientListScreen;
});
