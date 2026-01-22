odoo.define('aspl_gift_voucher.GiftVoucherLine', function(require) {
'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class GiftVoucherLine extends PosComponent {
        setup() {
            super.setup();
        }
        get highlight() {
            return this.props.gift_voucher !== this.props.selectedVoucher ? '' : 'highlight';
        }
    }
    GiftVoucherLine.template = 'GiftVoucherLine';

    Registries.Component.add(GiftVoucherLine);

    return GiftVoucherLine;
});