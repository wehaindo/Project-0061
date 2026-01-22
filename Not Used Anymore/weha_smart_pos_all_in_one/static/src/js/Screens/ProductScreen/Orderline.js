odoo.define('weha_pos.Orderline', function(require){
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Orderline = require('point_of_sale.Orderline');
    const {useListener} = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');


    const PosResOrderline = Orderline =>
        class extends Orderline {   

            onClickDelete(){
                this.trigger('delete-button', { orderline: this.props.line })
            }
            
        };

    Registries.Component.extend(Orderline, PosResOrderline);
    return Orderline;

});