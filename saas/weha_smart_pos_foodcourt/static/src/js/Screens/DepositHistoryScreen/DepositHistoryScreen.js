odoo.define('weha_smart_pos_foodcourt.DepositHistoryScreen', function (require) {
    'use strict';

    const { useExternalListener } = owl.hooks;
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    const { useState, useRef } = owl.hooks;


    class DepositHistoryScreen extends PosComponent{
        constructor(){
            super(...arguments);
            useExternalListener(window, 'keyup', this._cancelAtEscape);
            this.state = {
                records: this.get_sorted_records(),
                client: this.props.client
            };
        }
        get_sorted_records(){
            var sorted_records = _.sortBy(this.props.records, 'id').reverse();
            return sorted_records
        }
        _cancelAtEscape(event) {
            if (event.key === 'Escape') {
                this.showScreen('ProductScreen');
            }
        }
        get records() {
            return this.state.records;
        }
        back_screen(){
            this.showScreen('ProductScreen');
        }
        async print_ledger(){
            const { confirmed, payload: data } = await this.showPopup('PrintLedgerPopup', {
                                                    title: this.env._t('Deposit Ledger'),
                                                 });
            if(confirmed){
                let self = this;
                let domain = [['create_date', '>=', data.startDate  + " 00:00:00"],
                            ['create_date', '<=', data.endDate + " 23:59:59"],
                            ['customer_id','=',this.state.client.id]];
                this.DepositHistory(domain).then(function(res){
                    self.showScreen('ReceiptScreen', {'mode':'from_wallet', 'wallet':res});
                });
            }
        }
        async DepositHistory(domain){
            return await this.rpc({
                model: "pos.deposit",
                method: "search_read",
                domain : domain
            });
        }
    }
    DepositHistoryScreen.template = 'DepositHistoryScreen';
    DepositHistoryScreen.hideOrderSelector = true;

    Registries.Component.add(DepositHistoryScreen);

    return DepositHistoryScreen;
});
