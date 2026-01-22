/** @odoo-module **/

import { Dialog } from "@web/core/dialog/dialog";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, onWillStart, useState } from "@odoo/owl";

export class FingerDialog extends Component {
    setup() {
        this.recordId = this.props.recordId;
        this.rpc = useService("rpc");
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.state = useState({ error: true, message: "Try connecting to fingerprint device and waiting for fingerprint!", template: "" });
        onMounted(this.mounted);
    }

    async mounted(){
        var self = this;
        // self.state.message = "Connected to Fingerprint Device "   
        this.fingerData = await fetch("http://localhost:8001/enroll")  
        .then(response => response.json())
        .then(function(data){
            console.log(data);            
            if(data.status === 'Success'){
                self.state.error = false;
                self.state.message = "Scan Finger Successfully , Click Save Button to save fingerprint";
                self.state.template = data.template;
            }else{
                self.state.error = true;
                self.state.message = "Error Scan finger"   
            }            
        })
        .catch(function(error){
            self.state.message = "Error connect to fingerprint device" 
        });;
    }

    async onConfirm() {
        try {
            // Perform ORM write operation
            console.log(this.recordId);
            console.log(this.state.template);
            await this.orm.write("hr.employee", [this.recordId], {
                fingerprint_primary: this.state.template,  // Update the 'name' field
            });
            this.props.close();  // Close the dialog after updating
        } catch (error) {
            console.error("Failed to update record:", error);
        }        
    }
}

FingerDialog.components = { Dialog };

FingerDialog.template = "weha_smart_pos_aeon_pos_access_rights.FingerDialog";
