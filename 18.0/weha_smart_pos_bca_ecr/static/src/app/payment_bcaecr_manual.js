import { _t } from "@web/core/l10n/translation";
import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { serializeDateTime } from "@web/core/l10n/dates";
import { register_payment_method } from "@point_of_sale/app/store/pos_store";


const REQUEST_TIMEOUT = 10000;
const { DateTime } = luxon;

export class BcaecrManualPay extends PaymentInterface {
    setup(){
        super.setup(...arguments);
        this.processSuccess = false;
        this.cancelled = false;              
    }
    
    pending_bcaecrmanualpay_line() {
        return this.pos.getPendingPaymentLine("bcaecrmanualpay");
    }   

    send_payment_request(cid) {        
        super.send_payment_request(cid);
        console.log('Sending deposit payment request');            
        return this._process_bcaecrmanualpay(cid);
    }

    send_payment_cancel(order, cid) {
        super.send_payment_cancel(order, cid);
        console.log("Canceling bca ecr manual payment");        
        return this._bcaecrmanualpay_cancel();
    }   

    async _process_bcaecrmanualpay(cid) {
        console.log("Processing Bca Ecr Manual Pay");
        const order = this.pos.get_order();
        const paymentLine = order.get_selected_paymentline();
        paymentLine.set_payment_status("waitingInput");
        
        if (paymentLine.amount < 0) {
            if(!order._isRefundOrder()) {
                this._showError(_t("Cannot process transactions with negative amount."));
                return Promise.resolve();
            }   
        }        
        return this.start_get_status_polling();
    }

    _bcaecrmanualpay_cancel() {       
        console.log("Cancel Bca Ecr Manual Pay");  
        this.cancelled = true;      
        return Promise.resolve();
    }
    

    start_get_status_polling() {
        const self = this;        
        const res = new Promise(function (resolve, reject) {
            clearTimeout(self.polling);

            const check = () => {
                try {
                    self._poll_for_response(resolve, reject);
                } catch (err) {
                    clearInterval(self.polling);
                    reject(err);
                }
            };

            // check(); // immediate first
            self.polling = setInterval(check, 3000); // then every 3s
        });

        // cleanup always
        res.finally(() => {
            console.log("Finaly Polling");
            clearInterval(self.polling);
            self._reset_state();
        });

        return res;
    }

    _poll_for_response(resolve, reject) {
        console.log("Polling tick", new Date().toISOString());
        const self = this;
        console.log("Check Cancelled : " + self.cancelled);
        if (self.cancelled) {
            console.log("Polling stopped because cancelled");
            // clearInterval(self.polling);
            resolve(false);
            return;
        }

         // ✅ If success, stop polling and resolve
        console.log("Check Success : " + self.processSuccess);
        if (self.processSuccess) {
            self.processSuccess = false;
            // clearInterval(self.polling);
            resolve(true);
            return;
        }      

        const order = self.pos.get_order();
        const paymentLine = order.selected_paymentline;
        if (!paymentLine) {
            // clearInterval(self.polling);
            // resolve(false);
            return;
        }

                 
    }

    _reset_state(){     
        this.processSuccess = false;
        this.cancelled = false;       
        this.remaining_polls = 4;
        clearTimeout(this.polling);
    }

    _handle_odoo_connection_failure(data = {}) {
        // handle timeout
        const line = this.pending_bcaecrmanualpay_line();
        if (line) {
            line.set_payment_status("retry");
        }
        this._showError(
            _t(
                "Could not connect to the Odoo server, please check your internet connection and try again."
            )
        );
        return Promise.reject(data); // prevent subsequent onFullFilled's from being called
    }

    _showError(error_msg, title) {
        this.env.services.dialog.add(AlertDialog, {
            title: title || _t("Bca ECR Manual Pay Error"),
            body: error_msg,
        });
    }

}

register_payment_method("bcaecr_manual", BcaecrManualPay);