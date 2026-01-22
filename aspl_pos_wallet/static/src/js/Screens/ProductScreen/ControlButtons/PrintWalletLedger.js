odoo.define('aspl_pos_wallet.PrintWalletLedger', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class PrintWalletLedgerButton extends PosComponent {
        constructor() {
            super(...arguments);
        }
        async onClick(){
            const currentClient = this.env.pos.get_order().get_client();
            const rec = await this._getWalletRecords(currentClient.id);
            rec.length > 0 ? this.showScreen('WalletHistoryScreen', {records: rec, client:currentClient}) : false
        }
        async _getWalletRecords(partner_id) {
            var params = {
                 model: "wallet.management",
                 method: "search_read",
                 domain: [['customer_id', '=', partner_id]],
            }
            return await this.rpc(params);
        }
    }
    PrintWalletLedgerButton.template = 'PrintWalletLedgerButton';

    ProductScreen.addControlButton({
        component: PrintWalletLedgerButton,
        condition: function() {
            return this.env.pos.config.enable_wallet && this.env.pos.get_client();
        },
    });

    Registries.Component.add(PrintWalletLedgerButton);

    return PrintWalletLedgerButton;
});
