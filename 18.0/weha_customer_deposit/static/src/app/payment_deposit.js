import { _t } from "@web/core/l10n/translation";
import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { serializeDateTime } from "@web/core/l10n/dates";

const REQUEST_TIMEOUT = 10000;
const { DateTime } = luxon;

export class DepositPay extends PaymentInterface {
    setup(){
        super.setup(...arguments);
        this.pollingTimout = null;
        this.inactivityTimeout = null;
        this.queued = false;
        this.payment_stopped = false;
    }

    send_payment_request(cid) {
        super.send_payment_request(cid);
        console.log('Sending deposit payment request');
        return this._process_depositpay(cid);
    }

    pending_depositpay_line() {
        return this.pos.getPendingPaymentLine("depositpay");
    }

    send_payment_cancel(order, cid) {
        super.send_payment_cancel(order, cid);
        console.log("Canceling deposit payment");
        return this._depositpay_cancel();
    }

    _handle_odoo_connection_failure(data = {}) {
        // handle timeout
        const line = this.pending_depositpay_line();
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

    _depositpay_cancel() {
        // this._depositpay_handle_response(data);
        return Promise.resolve(true);        
    }

    _call_depositpay(data, action) {
        return this.env.services.orm.silent
            .call("pos.payment.method", action, [[this.payment_method_id.id], data])
            .catch(this._handle_odoo_connection_failure.bind(this));
    }

    async generate_deposit_change(amount){
        const order = this.pos.get_order();
        const partner = await order.get_partner();
        var values = {
          customer_id: partner.id,
          type: 'change',
          debit: amount
        }
        return this.env.services.orm.call(
            "customer.deposit",
            "create_from_ui",
            [],
            {values: values}
        ).then((response) => {
            console.log("Deposit change created:", response);
        }).catch(this._handle_odoo_connection_failure.bind(this));
    }

    async get_remaining_deposit_amount(amount) {
        const order = this.pos.get_order();
        const partner = await order.get_partner();
        if(!partner){
            this._showError(_t("Please select a customer."));
            return Promise.resolve(false);
        }
        return this.env.services.orm.call(
            "res.partner",
            "read",
            [[partner.id]],            
        ).then((partner) => {
            if (!partner || partner.length === 0) {
                this._showError(_t("No deposit found."));
                return Promise.resolve(0);
            }else{
                return partner[0].remaining_deposit_amount;
            }
        }).catch(this._handle_odoo_connection_failure.bind(this));
    }

    async _process_depositpay(cid) {
        const order = this.pos.get_order();
        const paymentLine = order.get_selected_paymentline();

        if (paymentLine.amount < 0) {
            if(!order._isRefundOrder()) {
                this._showError(_t("Cannot process transactions with negative amount."));
                return Promise.resolve();
            }   
        }

        var result = await this.get_remaining_deposit_amount(paymentLine.amount);
        console.log("Result : " + result);
        if (result) {            
            if (result < paymentLine.amount) {
                if(!order._isRefundOrder()) {
                    this._showError(_t("Insufficient deposit amount. Your current balance : " + result));
                    return Promise.resolve();
                }            
            }
            paymentLine.set_payment_status("done");
            await this.generate_deposit_change(paymentLine.amount)
            return Promise.resolve(true);
        }else{
            return Promise.resolve(false);
        }
    }

    _showError(error_msg, title) {
        this.env.services.dialog.add(AlertDialog, {
            title: title || _t("Deposit Pay Error"),
            body: error_msg,
        });
    }

}
