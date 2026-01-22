odoo.define('weha_smart_pos_foodcourt.DepositLedgerReceipt', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class DepositLedgerReceipt extends PosComponent {}
    DepositLedgerReceipt.template = 'DepositLedgerReceipt';

    Registries.Component.add(DepositLedgerReceipt);

    return DepositLedgerReceipt;
});
