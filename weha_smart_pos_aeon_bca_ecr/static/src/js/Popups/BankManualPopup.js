odoo.define('weha_smart_pos_aeon_bca_ecr.BankManualPopup', function(require) {
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
    class BankManualPopup extends AbstractAwaitablePopup {
        setup() {
            super.setup();
            this.state = useState({ cardNumberValue: '', expiredDateValue: '', merchantCodeValue: '', terminalIdValue: '', approvalCodeValue: ''});
            this.cardNumberRef = useRef('cardNumberRef');
            this.expiredDateRef = useRef('expiredDateRef');
            this.merchantCodeRef = useRef('merchantCodeRef');
            this.terminalIdRef = useRef('terminalIdRef');
            this.approvalCodeRef = useRef('approvalCodeRef')
            onMounted(this.onMounted);
        }

        onMounted() {
            this.cardNumberRef.el.focus();
        }

        getPayload() {
            return {
                cardnumber: this.state.cardNumberValue,
                expireddate: this.state.expiredDateValue,
                merchantcode: this.state.merchantCodeValue,
                terminalid: this.state.terminalIdValue,
                approvalcode: this.state.approvalCodeValue
            };
        }

        async confirm(){            
            if(this.state.cardNumberValue !== ""  && this.state.expiredDateValue !== ""  && this.state.merchantCodeValue !== "" && this.state.terminalIdValue !== ""  && this.state.approvalCodeValue !== ""){
                super.confirm();                
            }else{
                await this.handleClosingError("Please complete all information!")                
            }
        }

        async handleClosingError(message) {
            await this.showPopup('ErrorPopup', {title: 'Error', body: message});
        }
    }

    BankManualPopup.template = 'BankManualPopup';
    Registries.Component.add(BankManualPopup);

});
