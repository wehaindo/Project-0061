odoo.define('your_module.paymentline_note', function (require) {
    'use strict';

    const models = require('point_of_sale.models');

    // Extend Paymentline model
    const PaymentlineSuper = models.Paymentline;

    models.Paymentline = PaymentlineSuper.extend({
        initialize: function (attributes, options) {
            this.memo = '';
            console.log("extend initialize")
            return PaymentlineSuper.prototype.initialize.apply(this, arguments);
        },

        init_from_JSON: function (json) {
            PaymentlineSuper.prototype.init_from_JSON.apply(this, arguments);
            this.memo = json.memo || '';
            console.log("extend init_from_JSON")
        },

        export_as_JSON: function () {
            const json = PaymentlineSuper.prototype.export_as_JSON.apply(this, arguments);
            json.memo = this.memo || '';
            console.log("extend export_as_JSON")
            return json;
        },

        export_for_printing: function () {
            const json = PaymentlineSuper.prototype.export_for_printing.apply(this, arguments);
            this.memo = this.memo || json.memo || '';
            console.log("extend export_for_printing")
            return json;
        },

        // set_note: function (value) {
        //     this.note = value;
        //     this.trigger('change', this);
        // },
        //
        // get_note: function () {
        //     return this.note;
        // },
    });
});
