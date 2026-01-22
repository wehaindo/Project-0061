odoo.define('weha_smart_pos_disable_refund.RefundButton', function(require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const RefundButton  = require('point_of_sale.RefundButton');

    ProductScreen.addControlButton({
        component: RefundButton,
        condition: function() {
            return this.env.pos.config.is_show_refund_button
        },
        position: ['replace','RefundButton']
    });

});