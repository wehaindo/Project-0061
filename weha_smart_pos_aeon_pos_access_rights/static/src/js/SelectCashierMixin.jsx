/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { SelectCashierMixin } from "/pos_hr/static/src/js/SelectCashierMixin.js";


patch(SelectCashierMixin.prototype, 'SelectCashierMixin patch',{
    setup() {
        console.log("View Button Patch");        
        this._super.apply(this, arguments);       
    },    
    async askPin(){       
        console.log("AskPIN");    
    }
});



const patchMixin = require("web.patchMixin");
const PatchableMessage = patchMixin(components.Message);
const MessageList = require("mail/static/src/components/message_list/message_list.js");

PatchableMessage.patch(
    "owl_tutorial_extend_override_components/static/src/components/message/solution_3_patch_message.js",
    (T) => {    
        class MessagePatched extends T {      
            /**       
             * @override property       
              */      
            get avatar() {
                //  Code  your  override  here
            }
        }
        return MessagePatched;
    }
);
MessageList.components.Message  = PatchableMessage;