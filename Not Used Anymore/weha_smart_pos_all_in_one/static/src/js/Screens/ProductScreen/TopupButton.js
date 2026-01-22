odoo.define('weha_pos.TopupButton', function(require){
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const {useListener} = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class TopupButton extends PosComponent {
  
        async renderElement (){
            var self = this;
            var client = self.env.pos.get_client();
            if (client){
                self.showPopup('TopupPopupWidget', {});
            }else{
                const { confirmed, payload } = await this.showPopup('ConfirmPopup', {
                    title: this.env._t('Topup Wallet'),
                    body: this.env._t('Please tap wallet card first!'),
                });
            }
        }

    }

    TopupButton.template = 'TopupButtonWidget';
    Registries.Component.add(TopupButton);
    return TopupButton;

});