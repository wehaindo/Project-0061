/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";

import { sprintf } from "@web/core/utils/strings";
const { DateTime } = luxon;

export class PaymentDeposit extends PaymentInterface {
    setup() {
        super.setup(...arguments);
        this.paymentLineResolvers = {};
    }

    async send_payment_request(cid) {
        super.send_payment_request(cid);
        if(this.pos.get_order().get_partner()){
            var line  = this.pending_deposit_line()
            line.set_payment_status("waitingCard");
            const { confirmed , payload: value } = await this.env.services.popup.add(TextInputPopup, {
                title: 'Scan Card',
                placeholder: 'Please scan customer card or qrcode!',            
            });
            if (confirmed){
                console.log('confirm');
                console.log(value);
                await this._deposit_pay(value);
                if (line.get_payment_status() == 'done'){
                    return true;
                }
                // return true;                       
            }      
        }else{
            var line = this.pending_deposit_line();
            if (line) {
                line.set_payment_status("retry");
            }
            await this.env.services.popup.add(ErrorPopup, {
                title: 'Deposit Payment Error',
                body: 'Please assign customer for pay using deposit!',            
            });
        }
          
    }

    pending_deposit_line() {
        return this.pos.getPendingPaymentLine("deposit");
    }

    send_payment_cancel(order, cid) {
        super.send_payment_cancel(order, cid);    
    }

    async _deposit_pay(card_number){        
        try{
            var line  = this.pending_deposit_line();            
            const result = await this.get_remaining_deposit_amount(card_number);
            console.log(result);
            if (result){
                const data = result[0]
                console.log(data)
                if(line.amount < data['remaining_deposit_amount']){
                    const result = this.generate_deposit_change(line.amount)
                    line.set_payment_status("done");            
                }else{
                    line.set_payment_status("retry");
                    await this.env.services.popup.add(ErrorPopup, {
                        title: 'Deposit Payment Error',
                        body: 'Remaining amount not enough!',            
                    });               
                }
            }else{
                line.set_payment_status("retry");
                await this.env.services.popup.add(ErrorPopup, {
                    title: 'Deposit Payment Error',
                    body: 'No Deposit Balance Information!',            
                });
            }                                    
        }catch(err){
            console.log(err);
            var line = this.pending_deposit_line();
            if (line) {
                line.set_payment_status("retry");
            }
            await this.env.services.popup.add(ErrorPopup, {
                title: 'Deposit Payment Error',
                body: 'Process Deposit Payment Error!',            
            });
        }
    }

    async get_remaining_deposit_amount(card_number){
        let domain = [['card_number','=', card_number],['id','=',this.pos.get_order().get_partner().id]];
        console.log(domain);
        const result = await this.env.services.orm.searchRead("res.partner", domain, ["remaining_deposit_amount"])        
        return result;
    }
    
    async generate_deposit_change(amount){
        var values = {
          customer_id: this.pos.get_order().partner.id,
          type: 'change',
          debit: amount,          
        }
        const result = await this.env.services.orm.call("pos.deposit","create_from_ui",["",values])     
        return result;
    }
}