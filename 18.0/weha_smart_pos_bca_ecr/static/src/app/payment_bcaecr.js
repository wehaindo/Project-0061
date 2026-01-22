import { _t } from "@web/core/l10n/translation";
import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { serializeDateTime } from "@web/core/l10n/dates";
import { register_payment_method } from "@point_of_sale/app/store/pos_store";
import { BcaEcrMessageBuilder } from "../libs/BcaEcrMessageBuilder";
import { BcaEcrMessageParser } from "../libs/BcaEcrMessageParser";


const REQUEST_TIMEOUT = 10000;
const { DateTime } = luxon;

export class BcaecrPay extends PaymentInterface {
    setup(){
        super.setup(...arguments);
        this.pollingTimout = null;
        this.inactivityTimeout = null;
        this.queued = false;
        this.payment_stopped = false;
        this.processSuccess = false;
        this.cancelled = false;
        
        this.url = "ws://localhost:1337";   // your local payment device server
        this.ws = null;
        this.heartbeatInterval = null;
        this.requestId = 0;
        this.pendingRequests = {};

        this.connect();
    }

    connect() {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
            console.log("✅ WebSocket connected to POS Payment Device");
            this.startHeartbeat();
        };

        this.ws.onmessage = (event) => {
            console.log("📩 Message from device:", event.data);
            this.onMessage(event.data);
        };

        this.ws.onclose = () => {
            console.log("❌ WebSocket closed, retrying...");
            this.stopHeartbeat();
            setTimeout(() => this.connect(), 3000); // Auto reconnect
        };

        this.ws.onerror = (err) => {
            console.error("⚠️ WebSocket error:", err);
        };
    }

    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ action: "ping" }));
            }
        }, 10000); // send keepalive every 10s
    }

    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }

    onMessage(event) {
        console.log("Processing incoming message");
        var self = this;
        const order = this.pos.get_order();
        const paymentLine = order.get_selected_paymentline();
        let data = event;
        console.log("Data from Interface");
        console.log(data);                          
        //Parsing Response Message
        var parsing_data = this.parsing_ecr_response(data);
        if(parsing_data.resp_code === "3030"){
            console.log("Get 3030 Response")
            //QRIS Payment
            console.log(parsing_data.trans_type)            
            if(parsing_data.trans_type === "3331"){
                console.log('Receive Repsponse untuk Request 3331');     
                console.log('Response Code ' + parsing_data.resp_code);
                console.log('Trans Type ' + parsing_data.trans_type);
                console.log('Reff Number ' + this.hex_to_ascii(parsing_data.rrn));
                paymentLine.set_reff_number(this.hex_to_ascii(parsing_data.rrn));
                paymentLine.set_payment_line_status(paymentStatus.WAITING_QRIS);
                console.log("Close Connection untuk Request 3331")
            }else if(parsing_data.trans_type === "3031" ){
                //Success Payment
                console.log('Success Payment untuk 3031');                
                console.log('Response Code ' + parsing_data.resp_code);
                console.log('Trans Type ' + parsing_data.trans_type);
                console.log('Reff Number ' + this.hex_to_ascii(parsing_data.rrn));
                var jsonData = JSON.parse(data);
                // paymentLine.set_bca_ecr_data(jsonData.value);
                // paymentLine.set_reff_number(this.hex_to_ascii(parsing_data.rrn));
                // paymentLine.set_pan(this.hex_to_ascii(parsing_data.pan));
                // paymentLine.set_approval_code(this.hex_to_ascii(parsing_data.approval_code));
                // paymentLine.set_merchant_id(this.hex_to_ascii(parsing_data.marchant_id));
                // paymentLine.set_terminal_id(this.hex_to_ascii(parsing_data.terminal_id));
                // paymentLine.set_card_holder_name(this.hex_to_ascii(parsing_data.card_holder_name));
                paymentLine.bca_ecr_data = jsonData.value;
                paymentLine.reff_number = this.hex_to_ascii(parsing_data.rrn);
                paymentLine.pan = this.hex_to_ascii(parsing_data.pan);  
                paymentLine.approval_code = this.hex_to_ascii(parsing_data.approval_code);
                paymentLine.merchant_id = this.hex_to_ascii(parsing_data.marchant_id);
                paymentLine.terminal_id = this.hex_to_ascii(parsing_data.terminal_id);
                paymentLine.card_holder_name = this.hex_to_ascii(parsing_data.card_holder_name);                    
                console.log("change successEcr 3031");
                console.log(paymentLine);
                self.processSuccess = true;
                console.log("Close Connection untuk Request 3031")
            }else if(parsing_data.trans_type === "3332" ){
                //Success Payment
                console.log('Success Payment untuk 3332');                
                console.log('Response Code ' + parsing_data.resp_code);
                console.log('Trans Type ' + parsing_data.trans_type);
                console.log('Reff Number ' + self.hex_to_ascii(parsing_data.rrn));                  
                var jsonData = JSON.parse(data);
                // paymentLine.set_bca_ecr_data(jsonData.value);
                // paymentLine.set_reff_number(this.hex_to_ascii(parsing_data.rrn));
                // paymentLine.set_pan(this.hex_to_ascii(parsing_data.pan));
                // paymentLine.set_approval_code(this.hex_to_ascii(parsing_data.approval_code));
                // paymentLine.set_merchant_id(this.hex_to_ascii(parsing_data.marchant_id));
                // paymentLine.set_terminal_id(this.hex_to_ascii(parsing_data.terminal_id));
                // paymentLine.set_card_holder_name(this.hex_to_ascii(parsing_data.card_holder_name));
                paymentLine.bca_ecr_data = jsonData.value;
                paymentLine.reff_number = this.hex_to_ascii(parsing_data.rrn);
                paymentLine.pan = this.hex_to_ascii(parsing_data.pan);  
                paymentLine.approval_code = this.hex_to_ascii(parsing_data.approval_code);
                paymentLine.merchant_id = this.hex_to_ascii(parsing_data.marchant_id);
                paymentLine.terminal_id = this.hex_to_ascii(parsing_data.terminal_id);
                paymentLine.card_holder_name = this.hex_to_ascii(parsing_data.card_holder_name);
                console.log("change successEcr 3332");
                console.log(paymentLine);
                self.processSuccess = true;
                console.log("Close Connection untuk Request 3332")
            }else{                                                
                console.log("Transaction Type Not Recognized");
            }
        }else if(parsing_data.resp_code == "3534"){
            console.log('Decline Expired Card');
            if(paymentLine){
                paymentLine.set_payment_status('retry');       
                self.cancelled = true;         
            }           
        }else if(parsing_data.resp_code == "3535"){
            console.log('Decline Incorrect Pin');
            if(paymentLine){
                paymentLine.set_payment_status('retry');                
                self.cancelled = true;
            }           
        }else if(parsing_data.resp_code == "5032"){
            console.log('Read Card Error');
             if(paymentLine){
                paymentLine.set_payment_status('retry');                
                self.cancelled = true;
            }   
           
        }else if(parsing_data.resp_code == "5033"){
            console.log('Cancel Payment');
            if(paymentLine){
                paymentLine.set_payment_status('retry');   
                self.cancelled = true;             
            }                       
        }else if(parsing_data.resp_code == "5A33"){
            console.log('EMV Card Decline');
            if(paymentLine){
                paymentLine.set_payment_status('retry');                
                self.cancelled = true;
            }

        }else if(parsing_data.resp_code == "4345"){
            console.log('Connection Error/Line Busy');
            if(paymentLine){
                paymentLine.set_payment_status('retry');                
                self.cancelled = true;
            }

        }else if(parsing_data.resp_code == "544F"){
            console.log('Connection Timeout');
            if(paymentLine){
                paymentLine.set_payment_status('retry');                
                self.cancelled = true;
            }

        }else if(parsing_data.resp_code == "5054"){        
            console.log('Waiting QRIS Payment');
            if(parsing_data.trans_type == "3332"){
                self.set_payment_line_status(paymentStatus.WAITING_QRIS);
            }else{
                if(paymentLine){
                    paymentLine.set_payment_status('retry');                                        
                    self.cancelled = true;
                }
            }
        }else if(parsing_data.resp_code == "6161"){
            console.log('Decline (aa represent two digit alphanumeric value from EDC)');
            if(paymentLine){
                paymentLine.set_payment_status('retry');
                self.cancelled = true;
            }
           
        }else if(parsing_data.resp_code == "5332"){
            console.log('TRANSAKSI GAGAL ULANGI TRANSAKSI DI EDC');
            if(paymentLine){
                paymentLine.set_payment_status('retry');
                self.was_cancelled = true;
            }
           
        }else if(parsing_data.resp_code == "5333"){
            console.log('TXN BLM DIPROSES MINTA SCAN QR');
            if(paymentLine){
                paymentLine.set_payment_status('retry');
                self.cancelled = true;
            }
           
        }else if(parsing_data.resp_code == "5334"){
            console.log('TXN EXPIRED');
            if(paymentLine){
                paymentLine.set_payment_status('retry');
                self.cancelled = true;
            }
           
        }else if(parsing_data.resp_code == "544E"){
            console.log('Topup Tunai Not Ready');
            if(paymentLine){
                paymentLine.set_payment_status('retry');
                self.cancelled = true;
            }                      
        }else{
            console.log('Response Code ' + parsing_data.resp_code);
            if(paymentLine){
                paymentLine.set_payment_status('retry');
                self.cancelled = true;
            }
        }
    }

    hex_to_ascii(hex_data){
        var hex  = hex_data.toString();
        var str = '';
        for (var n = 0; n < hex.length; n += 2) {
            str += String.fromCharCode(parseInt(hex.substr(n, 2), 16));
        }
        return str;
    }

    getAmountPart(num) {       
          const amountStr = num.toString().split('.')[0];
          return amountStr;
    }
        
    getDecimalPart(num) {
          if (Number.isInteger(num)) {
            return "00";
          }        
          const decimalStr = num.toString().split('.')[1];
          if(parseInt(decimalStr) === 0){
            return "00"
          }
          if(decimalStr.length === 1){
            return decimalStr + "0";
          }
          return decimalStr;
    }

    _getArrInt(str){
        console.log(str);
        var myArray = str.match(/.{2}/g);
        var arrSend = [];
        for (var i = 0, l = myArray.length; i < l; i ++) {
            var hex_str = "0x" + myArray[i];
            var hex_int = parseInt(hex_str, 16);
            var new_int = hex_int + 0x200;
            arrSend.push(new_int);
        }        
        return arrSend;
    }

    _getBytesForLcr(message_length, ecr_version, str, end_of_text){
        let int_message_length = this._getArrInt(message_length);
        let int_ecr_version = this._getArrInt(ecr_version);
        let int_end_of_text = this._getArrInt(end_of_text);
        let intArray=str.split ('').map (function (c) { return c.charCodeAt (0); });  
        let concatArray = int_message_length.concat(int_ecr_version,intArray,int_end_of_text)
        let byteArray=new Uint8Array(concatArray.length);
        for (let i=0;i<concatArray.length;i++)
        byteArray[i]=concatArray[i];
        return byteArray;
    }

    _getBytesForMessage(start_of_text, message_length, ecr_version, str, end_of_text, lcr){
          let int_start_of_text = this._getArrInt(start_of_text);
          let int_message_length = this._getArrInt(message_length);
          let int_ecr_version = this._getArrInt(ecr_version);
          let int_end_of_text = this._getArrInt(end_of_text);    
          
          let intArray=str.split ('').map (function (c) { return c.charCodeAt (0); });    
          let concatArray = int_start_of_text.concat(int_message_length,int_ecr_version,intArray,int_end_of_text,lcr);
          console.log(concatArray);
          let byteArray=new Uint8Array(concatArray.length);
          for (let i=0;i<concatArray.length;i++)
            byteArray[i]=concatArray[i];
          return byteArray;
    }

    generate_ecr_message(trans_type, paymentLine){
        console.log('Generate ECR Message');
        var pan = '                   ';
        var expirydate = '    ';
        // if(paymentLine.payment_method.is_dev){            
        //     pan  = paymentLine.payment_method.pan + '   ';
        //     expirydate = paymentLine.payment_method.expirydate;
        // }
        console.log("paymentline.amount");
        console.log(paymentLine.amount);
        var amount = this.getAmountPart(paymentLine.amount)
        console.log("amount");
        console.log(amount);
        var decimal_amount = this.getDecimalPart(paymentLine.amount);
        console.log("decimal_amount");
        console.log(decimal_amount);
        var transaction_amount = amount.padStart(10,'0') + decimal_amount;
        console.log("transaction_amount");
        console.log(transaction_amount);
        var data = {
        start_of_text: '02', // 1 Digit (HEX)
        message_length: '0150',  // 4 Digit (HEX)
        ecr_version: '02', // (HEX)
        // transaction_type: paymentLine.payment_method.trans_type, // (ASCII) 2 Digit
        transaction_type: trans_type,
        // transaction_amount: '000000010000', // (ASCII) 12 Digit
        transaction_amount: transaction_amount,
        other_amount: '000000000000', // (ASCII) 12 Digit
        //pan: '5409120012345684   ', // (ASCII) 19 Digit
        //expire_date: '2510', // (ASCII) 4 Digit
        pan: pan, // (ASCII) 19 Digit
        expireddate: expirydate, // (ASCII) 4 Digit
        cancel_reason: '00', // (ASCII) 2 Digit
        invoice_reason: '000000', // (ASCII) 6 Digit
        auth_code: '      ', // (ASCII) 6 Digit
        installment_flag: ' ', // (ASCII) 1 Digit
        redeem_flag: ' ', // (ASCII) 1 Digit
        dcc_flag: 'N', // (ASCII) 1 Digit
        installment_plan: '   ', // (ASCII) 3 Digit
        installment_tenor: '  ', // (ASCII) 2 Digit
        generic_data: '            ', // (ASCII) 12 Digit
        refference_number: '000000000000', // (ASCII)  12 Digit
        original_date: '    ', // ASCII 4 Digit
        bca_filler: '                                                  ', // (ASCII) 50 Digit
        end_of_text: '03', // (HEX)
        }
        
        if(trans_type == '01' || trans_type == '31'){
            data.trans_type = trans_type;  
        }else if(trans_type == '32'){
        var data = {
            start_of_text: '02', // 1 Digit (HEX)
            message_length: '0150',  // 4 Digit (HEX)
            ecr_version: '03', // (HEX)
            transaction_type: trans_type, // (ASCII) 2 Digit
            transaction_amount: '000000000000', // (ASCII) 12 Digit
            other_amount: '000000000000', // (ASCII) 12 Digit
            pan: '                   ', // (ASCII) 19 Digit
            expireddate: '    ', // (ASCII) 4 Digit
            cancel_reason: '00', // (ASCII) 2 Digit
            invoice_reason: '000000', // (ASCII) 6 Digit
            auth_code: '      ', // (ASCII) 6 Digit
            installment_flag: ' ', // (ASCII) 1 Digit
            redeem_flag: ' ', // (ASCII) 1 Digit
            dcc_flag: 'N', // (ASCII) 1 Digit
            installment_plan: '   ', // (ASCII) 3 Digit
            installment_tenor: '  ', // (ASCII) 2 Digit
            generic_data: '            ', // (ASCII) 12 Digit
            refference_number: paymentLine.get_reff_number(), // (ASCII)  12 Digit
            original_date: '    ', // ASCII 4 Digit
            bca_filler: '                                                  ', // (ASCII) 50 Digit
            end_of_text: '03', // (HEX)        
        }
        // data.refference_number = paymentLine.get_reff_number();
        console.log("Get Reff Number");
        console.log(paymentLine.get_reff_number());
        }

        const data_in_str =                    
        data.transaction_type + 
        data.transaction_amount +  
        data.other_amount + 
        data.pan + 
        data.expireddate + 
        data.cancel_reason + 
        data.invoice_reason + 
        data.auth_code +
        data.installment_flag + 
        data.redeem_flag + 
        data.dcc_flag + 
        data.installment_plan + 
        data.installment_tenor +
        data.generic_data + 
        data.refference_number + 
        data.original_date + 
        data.bca_filler
        
        console.log("data_in_str");
        console.log(data_in_str);

        const data_for_lcr = this._getBytesForLcr(data.message_length, data.ecr_version, data_in_str, data.end_of_text);
        for (let i = 0; i < data_for_lcr.length; i++) {
            if (i == 0 ){
                var var1 = data_for_lcr[i];
            }else{
                var var1 = var1 ^ data_for_lcr[i];            
            }
        }

        const data_in_hex = this._getBytesForMessage(data.start_of_text, data.message_length, data.ecr_version, data_in_str, data.end_of_text, var1);
        var send_message = String
        var type = 'bca_ecr';          
        // console.log("Is Ether : " + paymentLine.payment_method.is_ether);
        // if (paymentLine.payment_method.is_ether === true){
        //     type = 'bca_ecr_ether';          
        // }          
        var message = {
            type: type,
            name: 'Payment BCA ECR',
            value: data_in_hex.join()
        };

        return message;
    }

    parsing_ecr_response(data){
        var jsonData = JSON.parse(data);
        console.log(jsonData);
        var resp_code = jsonData.value.slice(106,110);
        var trans_type = jsonData.value.slice(8,12);
        if (trans_type == "3031"){
        var parsing_data = {
            length: jsonData.value.slice(0,8), // 4
            trans_type: jsonData.value.slice(8,12), // 2
            trans_amount: jsonData.value.slice(12,36), // 12
            other_amount: jsonData.value.slice(36,60), // 12
            pan: jsonData.value.slice(60,98), // 19
            expiry_date: jsonData.value.slice(98,106), // 4
            resp_code: jsonData.value.slice(106,110), // 2
            rrn: jsonData.value.slice(110,134), // 12
            approval_code: jsonData.value.slice(134,146), // 6
            date: jsonData.value.slice(146,162), // 8
            time: jsonData.value.slice(162,174), // 6
            marchant_id: jsonData.value.slice(174,204), // 15
            terminal_id: jsonData.value.slice(204,220), // 8
            offline_flag: jsonData.value.slice(220,222), // 1
            card_holder_name: jsonData.value.slice(222,278), // 26
            pan_cashier_card: jsonData.value.slice(278,310), // 16
            invoice_number: jsonData.value.slice(310,322), // 6
            filler: jsonData.value.slice(322,338) // 8
        };
        }
        
        if (trans_type == "3331" || trans_type == "3332"){
        var parsing_data = {
            length: jsonData.value.slice(0,8), // 4
            trans_type: jsonData.value.slice(8,12), // 2
            trans_amount: jsonData.value.slice(12,36), // 12
            other_amount: jsonData.value.slice(36,60), // 12
            pan: jsonData.value.slice(60,98), // 19 - Benar
            expiry_date: jsonData.value.slice(98,106), // 4 
            resp_code: jsonData.value.slice(106,110), // 2
            rrn: jsonData.value.slice(110,134), // 12
            approval_code: jsonData.value.slice(134,146), // 6
            date: jsonData.value.slice(146,162), // 8  146 + 16 = 162
            time: jsonData.value.slice(162,174), // 6  162 + 12 = 174 
            marchant_id: jsonData.value.slice(180,210), // 15 
            terminal_id: jsonData.value.slice(210,226), // 8
            offline_flag: jsonData.value.slice(226,228), // 1
            card_holder_name: jsonData.value.slice(228,280), // 26 228 + 52
            pan_cashier_card: jsonData.value.slice(278,310), // 16
            invoice_number: jsonData.value.slice(310,322), // 6
            batch_number: jsonData.value.slice(322,334), // 6
            issuer_id: jsonData.value.slice(334,338), // 2
            installment_flag: jsonData.value.slice(338,440), // 1
            ddc_flag: jsonData.value.slice(440,442), // 1
            redeem_flag: jsonData.value.slice(442,444), // 1
            info_amount: jsonData.value.slice(444,468), // 12
            dcc_decimal_place: jsonData.value.slice(468,470), // 1
            ddc_currency_name: jsonData.value.slice(470,476), // 3
            ddc_ex_rate: jsonData.value.slice(476,492), // 8
            coupon_flag: jsonData.value.slice(492,494), // 1
            filler: jsonData.value.slice(494,510) // 8
        };
        }
        console.log("Parsing ECR Response")
        console.log(parsing_data);
        return parsing_data;
    }

    pending_bcaecrpay_line() {
        return this.pos.getPendingPaymentLine("bcaecrpay");
    }   

    send_payment_request(cid) {        
        super.send_payment_request(cid);
        console.log('Sending deposit payment request');            
        return this._process_bcaecrpay(cid);
    }

    send_payment_cancel(order, cid) {
        super.send_payment_cancel(order, cid);
        console.log("Canceling bca ecr payment");        
        return this._bcaecrpay_cancel();
    }   

    async _process_bcaecrpay(cid) {
        const builder = new BcaEcrMessageBuilder();
        const order = this.pos.get_order();
        const paymentLine = order.get_selected_paymentline();

        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {            
            this._showError(_t("Could not connect to the Payment Device, please ensure the device is connected and try again."));
            return Promise.resolve();
        }

        if (paymentLine.amount < 0) {
            if(!order._isRefundOrder()) {
                this._showError(_t("Cannot process transactions with negative amount."));
                return Promise.resolve();
            }   
        }        
        
        const id = order.name;
        var data = builder.generate_ecr_message("01", paymentLine);
        this.ws.send(JSON.stringify(data));
        console.log("Send Data to Web Socket");                
        return this.start_get_status_polling();        
    }
    
    _bcaecrpay_cancel() {       
        console.log("Cancel Bca Ecr Pay");  
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
        const line = this.pending_bcaecrpay_line();
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
            title: title || _t("Bca ECR Pay Error"),
            body: error_msg,
        });
    }

}

register_payment_method("bcaecr", BcaecrPay);