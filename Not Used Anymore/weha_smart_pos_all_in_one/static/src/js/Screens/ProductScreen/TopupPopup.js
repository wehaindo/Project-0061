odoo.define('weha_pos.TopupPopupWidget', function(require){
    "use strict";

    const Popup = require('point_of_sale.ConfirmPopup');
    const Registries = require('point_of_sale.Registries');
    const PosComponent = require('point_of_sale.PosComponent');

    class TopupPopupWidget extends Popup {
        constructor() {
            super(...arguments);
        }

        go_back_screen() {
            this.showScreen('ProductScreen');
            this.trigger('close-popup');
        }

    };
    
    TopupPopupWidget.template = 'TopupPopupWidget';
    Registries.Component.add(TopupPopupWidget);
    return TopupPopupWidget;

});