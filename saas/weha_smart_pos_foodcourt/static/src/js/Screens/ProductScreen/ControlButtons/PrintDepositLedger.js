odoo.define('weha_smart_pos_foodcourt.PrintDepositLedger', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class PrintDepositLedgerButton extends PosComponent {
        constructor() {
            super(...arguments);
        }
        async onClick(){
            const currentClient = this.env.pos.get_order().get_client();
            const rec = await this._getDepositRecords(currentClient.id);
            rec.length > 0 ? this.showScreen('DepositHistoryScreen', {records: rec, client:currentClient}) : false
        }
        async _getDepositRecords(partner_id) {
            var params = {
                 model: "post.deposit",
                 method: "search_read",
                 domain: [['customer_id', '=', partner_id]],
            }
            return await this.rpc(params);
        }
    }
    PrintDepositLedgerButton.template = 'PrintDepositLedgerButton';

    ProductScreen.addControlButton({
        component: PrintDepositLedgerButton,
        condition: function() {
            return this.env.pos.config.enable_deposit && this.env.pos.get_client();
        },
    });

    Registries.Component.add(PrintDepositLedgerButton);

    return PrintDepositLedgerButton;
});
