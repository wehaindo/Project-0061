odoo.define('weha_smart_pos_aeon_bca_ecr.PaymentBcaEcr', function(require){
    
    const core = require('web.core')
    const rpc = require('web.rpc')
    const PaymentInterface = require('point_of_sale.PaymentInterface')
    const { Gui } = require('point_of_sale.Gui')
  
    const paymentStatus = {
        PENDING: 'pending',
        RETRY: 'retry',
        WAITING: 'waiting',
        FORCE_DONE: 'force_done',
        WAITING_QRIS: 'waiting_qris'
    }

    const _t = core._t

    const PaymentBcaEcr = PaymentInterface.extend({
        
        init: function (pos, payment_method) {
          this._super(...arguments);
          this.successEcr = false;
          this.waitingEcr = false;
        },

        hex_to_ascii: function(hex_data){
          var hex  = hex_data.toString();
          var str = '';
          for (var n = 0; n < hex.length; n += 2) {
            str += String.fromCharCode(parseInt(hex.substr(n, 2), 16));
          }
          return str;
        },

        getAmountPart: function(num) {       
          const amountStr = num.toString().split('.')[0];
          return amountStr;
        },
        
        getDecimalPart: function(num) {
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
        },

        _getArrInt: function(str){
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
        },

        _getBytesForLcr: function(message_length, ecr_version, str, end_of_text){
          let int_message_length = this._getArrInt(message_length);
          let int_ecr_version = this._getArrInt(ecr_version);
          let int_end_of_text = this._getArrInt(end_of_text);
          let intArray=str.split ('').map (function (c) { return c.charCodeAt (0); });  
          let concatArray = int_message_length.concat(int_ecr_version,intArray,int_end_of_text)
          let byteArray=new Uint8Array(concatArray.length);
          for (let i=0;i<concatArray.length;i++)
            byteArray[i]=concatArray[i];
          return byteArray;
        },

        _getBytesForMessage: function(start_of_text, message_length, ecr_version, str, end_of_text, lcr){
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
        },

        generate_ecr_message: function(trans_type, paymentLine){
          console.log('Generate ECR Message');
          var pan = '                   ';
          var expirydate = '    ';
          if(paymentLine.payment_method.is_dev){            
            pan  = paymentLine.payment_method.pan + '   ';
            expirydate = paymentLine.payment_method.expirydate;
          }
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
          var message = {
            type: 'bca_ecr',
            name: 'Payment BCA ECR',
            value: data_in_hex.join()
          };

          return message;
        },

        // cardnumber, merchand code, approval code
        parsing_ecr_response: function(data){
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
        },

        //Send Data to ECR Interface
        send_data_to_web_socket: async function(data){
          var self = this;
          console.log("Start Connection to POS Interface");       
          this.counter = 0;
          this.pos_interface_conn = new WebSocket('ws://localhost:1337');                
          this.pos_interface_conn.onopen = function (e) {
              console.log("Connection to pos interface established!");
              this.pos_interface_conn_status = true;
              self.sendMessage(this.pos_interface_conn, JSON.stringify(data));                               
          };
           // callback messages
          this.pos_interface_conn.onmessage = function (e) {              
              console.log("Receive Message");
              console.log("Data from Interface");
              // Get Payment Line
              const order = self.pos.get_order();
              let paymentLine = order.selected_paymentline;
              //Get Incoming Data (Response Message)
              var data = e.data;
              console.log(data);                          
              //Parsing Response Message
              var parsing_data = self.parsing_ecr_response(data);
              console.log(parsing_data);
              //Check Respcode
              // 3030 is Success Response
              // 5033 is
              // 5054 is
              if(parsing_data.resp_code == "3030"){
                //QRIS Payment
                if(parsing_data.trans_type == "3331"){
                  console.log('Response Code ' + parsing_data.resp_code);
                  console.log('Trans Type ' + parsing_data.trans_type);
                  console.log('Reff Number ' + self.hex_to_ascii(parsing_data.rrn));
                  paymentLine.set_reff_number(self.hex_to_ascii(parsing_data.rrn));
                  self.set_payment_line_status(paymentStatus.WAITING_QRIS);
                }else{
                  console.log('Success Payment');
                  var jsonData = JSON.parse(data);
                  paymentLine.set_bca_ecr_data(jsonData.value);
                  paymentLine.set_reff_number(self.hex_to_ascii(parsing_data.rrn));
                  paymentLine.set_pan(self.hex_to_ascii(parsing_data.pan));
                  paymentLine.set_approval_code(self.hex_to_ascii(parsing_data.approval_code));
                  paymentLine.set_merchant_id(self.hex_to_ascii(parsing_data.marchant_id));
                  paymentLine.set_terminal_id(self.hex_to_ascii(parsing_data.terminal_id));
                  paymentLine.set_card_holder_name(self.hex_to_ascii(parsing_data.card_holder_name));                                    
                  self.successEcr = true;
                }
              }else if(parsing_data.resp_code == "3534"){
                console.log('Decline Expired Card');
                paymentLine.set_payment_status('retry');
                self.was_cancelled = true;  
              }else if(parsing_data.resp_code == "3535"){
                console.log('Decline Incorrect Pin');
                paymentLine.set_payment_status('retry');
                self.was_cancelled = true;  
              }else if(parsing_data.resp_code == "5032"){
                console.log('Read Card Error');
                paymentLine.set_payment_status('retry');
                self.was_cancelled = true;  
              }else if(parsing_data.resp_code == "5033"){
                console.log('Cancel Payment');
                paymentLine.set_payment_status('retry');
                self.was_cancelled = true;
              }else if(parsing_data.resp_code == "5A33"){
                console.log('EMV Card Decline');
                paymentLine.set_payment_status('retry');
                self.was_cancelled = true;  
              }else if(parsing_data.resp_code == "4345"){
                console.log('Connection Error/Line Busy');
                paymentLine.set_payment_status('retry');
                self.was_cancelled = true;             
              }else if(parsing_data.resp_code == "544F"){
                console.log('Connection Timeout');
                paymentLine.set_payment_status('retry');
                self.was_cancelled = true;             
              }else if(parsing_data.resp_code == "5054"){
                console.log('Waiting QRIS Payment');
                if(parsing_data.trans_type == "3332"){
                  self.set_payment_line_status(paymentStatus.WAITING_QRIS);        
                }else{
                  paymentLine.set_payment_status('retry');  
                  self.was_cancelled = true;
                }
              }else if(parsing_data.resp_code == "6161"){
                console.log('Decline (aa represent two digit alphanumeric value from EDC)');
                paymentLine.set_payment_status('retry');
                self.was_cancelled = true; 
              }else if(parsing_data.resp_code == "5332"){
                console.log('TRANSAKSI GAGAL ULANGI TRANSAKSI DI EDC');
                paymentLine.set_payment_status('retry');
                self.was_cancelled = true; 
              }else if(parsing_data.resp_code == "5333"){
                console.log('TXN BLM DIPROSES MINTA SCAN QR');
                paymentLine.set_payment_status('retry');
                self.was_cancelled = true; 
              }else if(parsing_data.resp_code == "5334"){
                console.log('TXN EXPIRED');
                paymentLine.set_payment_status('retry');
                self.was_cancelled = true; 
              }else if(parsing_data.resp_code == "544E"){
                console.log('Topup Tunai Not Ready');
                paymentLine.set_payment_status('retry');
                self.was_cancelled = true;                 
              }else{
                console.log('Response Code ' + parsing_data.resp_code);
                paymentLine.set_payment_status('retry');
                self.was_cancelled = true;
              }
          };
          // close 
          this.pos_interface_conn.onclose = function (e){
              console.log("Close Session");
          }   
        },

        waitForSocketConnection: function(socket, callback){
          setTimeout(
              function () {
                  if (socket.readyState === 1) {
                      console.log("Connection is made")
                      if (callback != null){
                          callback();
                      }
                  } else {
                      console.log("wait for connection...")
                      this.waitForSocketConnection(socket, callback);
                  }
              }, 10); // wait 5 milisecond for the connection...
        },

        sendMessage: function(socket, data) {
          var self = this;
          console.log("_sendMessage");
          this.waitForSocketConnection(this.pos_interface_conn, function(){
              console.log("message sent!!!");
              self.pos_interface_conn.send(data);
          });
        },

        set_payment_line_status: function(status){
          const order = this.pos.get_order()
          let paymentLine = order.selected_paymentline;
          paymentLine.set_payment_status(status)
        },

        send_payment_request: function () {
            // var data = '01000000572500000000000000 000000000000 N';
            this._super.apply(this, arguments)
            this._reset_state();
            return this._bca_ecr_pay();
        },

        check_payment_qris: function(){
          return this._bca_ecr_qris_check();
        },
        
        send_payment_cancel: function (order, cid) {
            this._super.apply(this, arguments);
            //this.pos_interface_conn.close();
            return Promise.resolve();
        },

        close: function () {
            this._super.apply(this, arguments);
        },

        _reset_state: function () {
            this.was_cancelled = false;
            this.remaining_polls = 4;
            clearTimeout(this.polling);
        },

        _handle_odoo_connection_failure: function (data) {
            // handle timeout
            const order = this.pos.get_order()
            let paymentLine = order.selected_paymentline;
            if (paymentLine) {
              paymentLine.set_payment_status(paymentStatus.RETRY)
            }
            this._show_error(_t('Could not connect to the Odoo server, please check your internet connection and try again.'))
            return Promise.reject(data) // prevent subsequent onFullFilled's from being called
          },

        _bca_ecr_pay: function () {
            console.log('_bca_ecr_pay');
            const self = this;
            const order = this.pos.get_order();
            let paymentLine = order.selected_paymentline;
            if (paymentLine && paymentLine.amount <= 0) {
              this._show_error(
                _t('Cannot process transaction with zero or negative amount.')
              )
              return Promise.resolve();
            }

            var data = this.generate_ecr_message(paymentLine.payment_method.trans_type, paymentLine);
            this.send_data_to_web_socket(data);
            this.set_payment_line_status(paymentStatus.WAITING);
            
            // const receipt_data = order.export_for_printing()
            // receipt_data.amount = paymentLine.amount
            // receipt_data.terminal_id = paymentLine.payment_method.xendit_pos_terminal_identifier
      
            return this.start_get_status_polling();
          },
        
        _bca_ecr_qris_check: function(){
          console.log('_bca_ecr_qris_check');
          const self = this;
          const order = this.pos.get_order();
          let paymentLine = order.selected_paymentline;
          if (paymentLine && paymentLine.amount <= 0) {
            this._show_error(
              _t('Cannot process transaction with zero or negative amount.')
            )
            return Promise.resolve();
          }
          var data = this.generate_ecr_message('32', paymentLine);
          this.send_data_to_web_socket(data);
          this.set_payment_line_status(paymentStatus.WAITING);    
          return this.start_get_status_polling();
        },

        start_get_status_polling () {
            const self = this
            const res = new Promise(function (resolve, reject) {
              clearTimeout(self.polling)
              self._poll_for_response(resolve, reject)
              self.polling = setInterval(function () {
                self._poll_for_response(resolve, reject)
              }, 5500)
            })
      
            // make sure to stop polling when we're done
            res.finally(function () {
              self._reset_state()
            })
      
            Promise.resolve()
            return res
        },

        _poll_for_response: function (resolve, reject) {
            const self = this
            
            if (this.was_cancelled) {
              resolve(false)
              return Promise.resolve()
            }
      
            const order = this.pos.get_order()
            const paymentLine = order.selected_paymentline;
      
            // If the payment line dont have xendit invoice then stop polling retry.
            if (!paymentLine) {
              resolve(false)
              return Promise.resolve()
            }

            // if (this.counter == 10){
            //   this.counter = 0;
            //   console.log(this.counter);
            //   resolve(true)
            //   return Promise.resolve()
            // }
            // this.counter = this.counter + 1;

            console.log('successECR 1');
            console.log(this.successEcr);

            if(this.successEcr){
              console.log("Success Payment 2");
              this.successEcr = false;
              console.log('successECR 2');
              console.log(this.successEcr);
              resolve(true)
              return Promise.resolve();
            }

        },  
    });

    return PaymentBcaEcr    
});
