/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { onMounted } from "@odoo/owl";

export class PaymentMethodPopup extends AbstractAwaitablePopup {
    static template = "weha_smart_pos_base.PaymentMethodPopup";
    static defaultProps = {
        cancelText: _t("Cancel"),
        title: _t("Payment Methods"),
        confirmKey: false,        
        paymentMethods: [],        
    };

    setup() {
        super.setup();        
        this.parent = this.props.parent;        
    }
}
