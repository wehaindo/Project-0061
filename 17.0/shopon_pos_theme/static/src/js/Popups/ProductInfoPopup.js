/** @odoo-module */

import Registries from 'point_of_sale.Registries';
import { patch } from "@web/core/utils/patch";

patch(Registries.Component.baseNameMap.ProductInfoPopup.prototype, 'ProductInfoPopupDAH',{
    _hasMarginsCostsAccessRights() {
            const isAccessibleToEveryUser = this.env.pos.config.is_margins_costs_accessible_to_every_user;
            const isCashierManager = this.env.pos.get_cashier().role === 'manager';
            return (isAccessibleToEveryUser || isCashierManager) && !this.env.pos.config.setu_is_hide_financial_details;
    }
})
