odoo.define('aspl_pos_wallet.WalletHistoryList', function (require) {
    'use strict';

    const { useContext } = owl.hooks;
    const { useAutofocus, useListener } = require('web.custom_hooks');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const OrderFetcher = require('point_of_sale.OrderFetcher');
    const contexts = require('point_of_sale.PosContext');


    class WalletHistoryList extends PosComponent {}
    WalletHistoryList.template = 'WalletHistoryList';

    Registries.Component.add(WalletHistoryList);

    return WalletHistoryList;
});

