/** @odoo-module */

import { Component } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";
import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { TextAreaPopup } from "@point_of_sale/app/utils/input_popups/textarea_popup";


export class SupportChannelButton extends Component {
    static template = "weha_smart_pos_base.SupportChannelButton";

    setup() {
        this.pos = usePos();
        this.ui = useState(useService("ui"));
        this.orm = useService("orm");
        this.popup = useService("popup");
        this.notification = useService("notification");    
    }

    async onClick() {
        console.log("Click SupportChannelButton");
        // console.log(this.pos.pos_session);
        console.log(this.pos.config);
        console.log(this.pos.discuss_channels)

        const discuss_channels = this.pos.discuss_channels;
        const selectionList = discuss_channels.map((channel) => ({
            id: channel.id,
            label: channel.name,
            isSelected: false,
            item: channel,
        }));   

        const { confirmed, payload: selectedSupportChannel } = await this.popup.add(SelectionPopup, {
            title: _t("Select Support Channel"),
            list: selectionList,
        });

        if (confirmed) {
            console.log(selectedSupportChannel);                   
            const { confirmed, payload: payloadMessage } = await this.popup.add(TextAreaPopup, {
                title: _t("Support Message"),                                
            });
            if(confirmed){
                console.log(payloadMessage);                
                var message  = 'From ' +  this.pos.config.current_user_id[1] + " : " + payloadMessage
                const result = await this.orm.call("pos.session", "send_message_to_channel",[selectedSupportChannel.id,message]);                
            }
        }
    }
}


Navbar.components = { ...Navbar.components,SupportChannelButton };