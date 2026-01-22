odoo.define('aspl_pos_wallet.WalletLedgerReceipt', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class WalletLedgerReceipt extends PosComponent {}
    WalletLedgerReceipt.template = 'WalletLedgerReceipt';

    Registries.Component.add(WalletLedgerReceipt);

    return WalletLedgerReceipt;
});
