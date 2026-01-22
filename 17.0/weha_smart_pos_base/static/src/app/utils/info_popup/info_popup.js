/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { onMounted } from "@odoo/owl";

export class InfoPopup extends AbstractAwaitablePopup {
    static template = "weha_smart_pos_base.InfoPopup";
    static defaultProps = {
        confirmText: _t("Ok"),
        title: _t("Information"),
        cancelKey: false,
        sound: true,
    };

    setup() {
        super.setup();
        onMounted(this.onMounted);
        this.sound = useService("sound");
    }
    onMounted() {
        if (this.sound) {
            this.sound.play("error");
        }
    }
}
