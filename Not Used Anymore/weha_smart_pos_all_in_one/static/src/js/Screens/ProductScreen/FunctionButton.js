odoo.define('weha_pos.FunctionButton', function(require){
    'use strict';
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const {useListener} = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class FunctionButton extends PosComponent {
        constructor(){
            super(...arguments);
            useListener('click', this.onClick);
        }

        async onClick() {
            await this.showTempScreen('FunctionScreen', );
        }
    }

    FunctionButton.template = 'PosFunctionWidget'

    // ProductScreen.addControlButton({
    //     component: FunctionButton,
    //     condition: function (){
    //         return true;
    //     },
    //     position: ['before','SetPricelistButton'],
    // });

    Registries.Component.add(FunctionButton);
    return FunctionButton;

})