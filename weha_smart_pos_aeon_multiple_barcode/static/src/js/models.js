odoo.define('weha_smart_pos_aeon_multiple_barcode.models', function(require){
    "use strict";

    var models = require('point_of_sale.models');
    var { PosCollection, PosModel, PosGlobalState, Order, Orderline, Product } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');


    const MultipleBarcodePosGlobalState = (PosGlobalState) => 
    class  extends PosGlobalState {
        constructor(obj) {
            super(obj);
        }
    }
});