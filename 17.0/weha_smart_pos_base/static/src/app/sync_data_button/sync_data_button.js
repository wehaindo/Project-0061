/** @odoo-module */

import { Component } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";
import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { InfoPopup } from "@weha_smart_pos_base/app/utils/info_popup/info_popup";


export class SyncDataButton extends Component {
    static template = "weha_smart_pos_base.SupportChannelButton";

    setup() {
        this.pos = usePos();
        this.ui = useState(useService("ui"));
        this.orm = useService("orm");
        this.popup = useService("popup");
        this.notification = useService("notification");    
    }

    async onClick() {
        console.log("Click SyncDataButton");
        const { confirmed } = await this.popup.add(ConfirmPopup, {
            title: _t("Sync Data from Server"),
            body: _t("Are you sure to sync data from server now?")                    
        });
        if (confirmed) {
            const products = await this.orm.call("pos.config", "prepare_sync_data",[this.pos.config.id]);                            
            for (var i = 0, len = products.length; i < len; i++) {
                this.pos.db.remove_products(products[i].id);
            }                        
            await this.pos._loadProductProduct(products);
            this.pos.popup.add(InfoPopup, {
                title: _t("Sync Data Finish"),
                body: _t("Sync Products : " + products.length.toString()),
            });
        }
    }
}


Navbar.components = { ...Navbar.components,SyncDataButton };