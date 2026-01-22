odoo.define('kaz_actan_pos_barecode.pos', function (require) {
"use strict";

var { Order } = require('point_of_sale.models');
var Registries = require('point_of_sale.Registries');

const PosReceiptBarcode = (Order) => class PosReceiptBarcode extends Order {
    export_for_printing() {
        var result = super.export_for_printing(...arguments);
        var canvas = document.createElement('canvas');
        JsBarcode(canvas, result.name);
        result['barcode'] = canvas.toDataURL("image/png");
        return result;
    }
}
Registries.Model.extend(Order, PosReceiptBarcode);

});


