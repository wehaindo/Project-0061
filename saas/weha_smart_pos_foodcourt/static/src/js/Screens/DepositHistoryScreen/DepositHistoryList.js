odoo.define('weha_smart_pos_foodcourt.DepositHistoryList', function (require) {
    'use strict';

    const { useContext } = owl.hooks;
    const { useAutofocus, useListener } = require('web.custom_hooks');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const OrderFetcher = require('point_of_sale.OrderFetcher');
    const contexts = require('point_of_sale.PosContext');


    class DepositHistoryList extends PosComponent {}
    DepositHistoryList.template = 'DepositHistoryList';

    Registries.Component.add(DepositHistoryList);

    return DepositHistoryList;
});

