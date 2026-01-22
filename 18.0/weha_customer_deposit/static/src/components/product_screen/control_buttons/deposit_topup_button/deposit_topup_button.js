import { _t } from "@web/core/l10n/translation";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
import { useService } from "@web/core/utils/hooks";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";

export class DepositTopupButton extends Component {
    static template = "point_of_sale.DepositTopupButton";
    static props = {
        icon: { type: String, optional: true },
        label: { type: String, optional: true },        
        class: { type: String, optional: true },
    };
    static defaultProps = {
        label: _t("Deposit Top-Up"),        
        class: "",
    };

    setup() {
        this.pos = usePos();
        this.dialog = useService("dialog");
    }

    onClick() {
        return this.props.label == _t("General Note") ? this.addGeneralNote() : this.addLineNotes();
    }
    
}