/** @odoo-module **/

import { registry } from "@web/core/registry";
import { FingerDialog } from "./FingerDialog";
import { useService } from "@web/core/utils/hooks";

function OpenFingerDialog(env, action) {
    const dialog = env.services.dialog;
    const recordId = action.params ? action.params.record_id : null;
    dialog.add(FingerDialog, { 
        recordId,
        close: () => dialog.close()
    });
    return Promise.resolve();
}

registry.category("actions").add("action_open_finger_dialog", OpenFingerDialog);
