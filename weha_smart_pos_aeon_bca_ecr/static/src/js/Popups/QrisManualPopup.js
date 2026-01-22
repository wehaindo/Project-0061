odoo.define('weha_smart_pos_aeon_bca_ecr.QrisManualPopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { onMounted, useRef, useState } = owl;

    /**
     * Props:
     *  {
     *      info: {object of data}
     *  }
     */

    class QrisManualPopup extends AbstractAwaitablePopup {
        setup() {
            super.setup();
            this.state = useState({ merchantCodeValue: '', terminalIdValue: '', approvalCodeValue: ''});
            this.merchantCodeRef = useRef('merchantCodeRef');
            this.terminalIdRef = useRef('terminalIdRef');
            this.approvalCodeRef = useRef('approvalCodeRef')
            onMounted(this.onMounted);
        }

        onMounted() {
            this.merchantCodeRef.el.focus();
        }

        async confirm(){            
            if(this.state.merchantCodeValue !== "" && this.state.terminalIdValue !== ""  && this.state.approvalCodeValue !== ""){
                super.confirm();                
            }else{
                await this.handleClosingError("Please complete all information!")                
            }
        }

        async handleClosingError(message) {
            await this.showPopup('ErrorPopup', {title: 'Error', body: message});
        }
        
        getPayload() {
            return {
                merchantcode: this.state.merchantCodeValue,
                terminalid: this.state.terminalIdValue,
                approvalcode: this.state.approvalCodeValue
            };
        }
    }

    QrisManualPopup.template = 'QrisManualPopup';    
    Registries.Component.add(QrisManualPopup);

});
