odoo.define('weha_pos.RefundButton',  function(require){
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const ButtonList = require('weha_pos.ButtonList');
    const {useListener} = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');


    class RefundButton extends PosComponent {
        constructor(){
            super(...arguments);
            useListener('click', this.onClick);
        }   

        async onClick(){
            
        }

    }

    RefundButton.template = 'RefundButtonWidget';
    Registries.Component.add(RefundButton);
    return RefundButton;

});