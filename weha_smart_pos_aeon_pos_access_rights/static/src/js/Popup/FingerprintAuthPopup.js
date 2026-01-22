odoo.define('weha_smart_pos_access_rights.FingerprintAuthPopup', function (require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { onMounted, useRef, useState } = owl;


    class FingerprintAuthPopup extends AbstractAwaitablePopup {
        setup(){
            super.setup();
            this.state = useState({ message: "Try connecting to fingerprint device and waiting for fingerprint!", error:false, status:false});            
            onMounted(this.mounted);
        }

        async mounted(){
            try {
                console.log(this.props.employee);                
                this.state.message = "Waiting for your fingerprint...";
                const randomString = Math.random().toString(36).substring(2);
                const response = await fetch("http://localhost:8000/verify?template=" + this.props.employee.fingerprint_primary + "&randomstring=" + randomString );
                console.log(response.status);
                if (!response.ok) {
                    console.log(response.status);
                }
                const json = await response.json();
                if(json.message == 'Success'){
                    console.log("Success");   
                    if(json.data == randomString){  
                        this.state.message = "Fingerprint Verified!";      
                        this.state.status = true;              
                        this.confirm();
                    }else{
                        this.state.error = true;
                        this.state.message = "Fingerprint Verify Failed!, Try Again.";
                    }
                }else{
                    this.state.error = true;
                    this.state.message = "Fingerprint Verify Failed!, Try Again.";
                }
                console.log(json);
            } catch (error) {
                console.log(error.message);
                this.state.error = true;
                this.state.message = "Error connect to Fingerprint Service!";            
            }
        }

        async handleClosingError(message) {
            await this.showPopup('ErrorPopup', {title: 'Error', body: message});
        }      

        getPayload() {            
            return this.state.status;
        }
        
    }

    FingerprintAuthPopup.template = 'FingerprintAuthPopup';
    FingerprintAuthPopup.defaultProps = {
        body: '',
    };
    Registries.Component.add(FingerprintAuthPopup);

    return FingerprintAuthPopup;

});