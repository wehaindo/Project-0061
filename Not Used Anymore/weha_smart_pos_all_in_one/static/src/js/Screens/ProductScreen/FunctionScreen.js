odoo.define('weha_pos.FunctionScreen', function(require){
    'use strict';
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const {useListener} = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class FunctionScreen extends PosComponent {

        back(){
            this.trigger('close-temp-screen');
        }

    }

    FunctionScreen.template = 'FunctionScreen';
    Registries.Component.add(FunctionScreen);
    return FunctionScreen;

})