odoo.define('weha_smart_pos_aeon_mandiri_ecr.PaymentMandiriEcr', function(require){
    
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

    const PaymentMandiriEcr = PaymentInterface.extend({
        
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
        
        string_to_hex(str) {
          var hex = '';
          for(var i=0;i<str.length;i++) {
              hex += ''+str.charCodeAt(i).toString(16);
          }
          return hex;
        },


        _getCrc: function(longString){
            // Define a long string of digits
            // const longString = "01313030303030303030303530303030303030303030303030303003";

            // Initialize a variable to store the cumulative XOR result
            let cumulativeXor = 0;

            // Loop through the string in steps of 2
            for (let i = 0; i < longString.length; i += 2) {
                // Take a two-digit segment
                const segment = longString.slice(i, i + 2);
                
                // Convert the segment to an integer
                const num = parseInt(segment, 16);
                
                // Perform XOR with the cumulative result
                cumulativeXor ^= num;
            }

            // Print the final XOR result
            console.log(cumulativeXor);
            return cumulativeXor.toString(16).padStart(2, '0');

        },

        parsing_mandiri_ecr_response: function(data){
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
        },

        generate_mandiri_ecr_message(transType, paymentLine){
            console.log('Generate ECR Message');
            console.log("paymentline.amount");
            console.log(paymentLine.amount);
            var amount = paymentLine.amount.toString();
            const str_amount = amount.padStart(12,'0') + ''.padStart(12,'0');            
            var for_crc = "01" + transType + this.string_to_hex(str_amount) + "03";
            var crc = this._getCrc(for_crc);
            var str = "0201" + transType + this.string_to_hex(str_amount) + "03" + crc;
            console.log(str);
            var type = 'mandiri_ecr';          
            console.log("Is Ether : " + paymentLine.payment_method.is_ether);
            if (paymentLine.payment_method.is_ether === true){
              type = 'mandiri_ecr_ether';          
            }          
            var message = {
              type: type,
              name: 'Payment Mandiri ECR',
              // value: "020131303030303030303030353030300306"
              value: str
            };
            return message;
        },

        // set_payment_line_status: function(status){
        //     const order = this.pos.get_order()
        //     let paymentLine = order.selected_paymentline;
        //     paymentLine.set_payment_status(status)
        // },

        send_payment_request: async function() {
            await this._super.apply(this, arguments);                 
            // this.set_payment_line_status('waiting');          
            this._reset_state();
            return this._mandiri_ecr_pay();
        },


        parsing_ecr_response: function(data){
          var jsonData = JSON.parse(data);
          console.log(jsonData);
          var resp_code = jsonData.value.slice(106,110);
          var trans_type = jsonData.value.slice(4,8);
          var data = jsonData.value.slice(12, jsonData.value.length - 4);
          console.log(trans_type);
          data_ascii = this.hex_to_ascii(data);
          arr_data_ascii = data_ascii.split("|");
          var parsing_data = {
              header: jsonData.value.slice(0,4),
              trans_type: jsonData.value.slice(4,8),
              bit_39: jsonData.value.slice(8,12),
              data: jsonData.value.slice(12, jsonData.value.length - 4),     
              terminal_id: arr_data_ascii[0],
              merchant_id: arr_data_ascii[1],
              jenis_kartu: arr_data_ascii[2],        
              pan: arr_data_ascii[3],
              mode_entry: arr_data_ascii[4],
              jenis_transaksi: arr_data_ascii[5],
              nomor_batch: arr_data_ascii[6],
              nomor_trace: arr_data_ascii[7],
              tanggal: arr_data_ascii[8],
              waktu: arr_data_ascii[9],
              kode_referensi: arr_data_ascii[10],
              kode_approval: arr_data_ascii[11],
              total_amount: arr_data_ascii[12],
              stop_tag: jsonData.value.slice(jsonData.value.length - 4, jsonData.value.length - 2),       
              crc: jsonData.value.slice(jsonData.value.length - 2, jsonData.value.length),       
          };                         
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
                var parsing_data = self.parsing_ecr_response(data);                
                if(parsing_data.trans_type === "3130"){
                  if(parsing_data.bit_39 == "3030"){
                    console.log('Sucesss');
                    paymentLine.set_bca_ecr_data(data);
                    paymentLine.set_reff_number(parsing_data.kode_referensi);
                    paymentLine.set_pan(parsing_data.pan);
                    paymentLine.set_approval_code(parsing_data.kode_approval);
                    paymentLine.set_merchant_id(parsing_data.merchant_id);
                    paymentLine.set_terminal_id(parsing_data.terminal_id);                    
                    self.successEcr = true;  
                    self.pos_interface_conn.close();
                  }
                  if(parsing_data.bit_39 != "3030"){
                    console.log('Error');
                    paymentLine.set_payment_status('retry');
                    self.was_cancelled = true;  
                    self.pos_interface_conn.close();
                  }
                }

                if(parsing_data.trans_type === "3c30"){
                  if(parsing_data.bit_39 == "3030"){
                    console.log('Sucesss');
                    paymentLine.set_bca_ecr_data(data);
                    paymentLine.set_reff_number(parsing_data.kode_referensi);
                    paymentLine.set_pan(parsing_data.pan);
                    paymentLine.set_approval_code(parsing_data.kode_approval);
                    paymentLine.set_merchant_id(parsing_data.merchant_id);
                    paymentLine.set_terminal_id(parsing_data.terminal_id);                    
                    self.successEcr = true;  
                    self.pos_interface_conn.close();
                  }
                  if(parsing_data.bit_39 != "3030"){
                    console.log('Error');
                    paymentLine.set_payment_status('retry');
                    self.was_cancelled = true;  
                    self.pos_interface_conn.close();
                  }
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

        send_payment_cancel: function (order, cid) {
          this._super.apply(this, arguments);
          if(this.pos_interface_conn){
              this.pos_interface_conn.close();
          }            
          return Promise.resolve();
        },

        _mandiri_ecr_pay: function () {
            console.log('_mandiri_ecr_pay');
            const self = this;
            const order = this.pos.get_order();
            let paymentLine = order.selected_paymentline;
            if (paymentLine && paymentLine.amount <= 0) {
              this._show_error(
                _t('Cannot process transaction with zero or negative amount.')
              )
              return Promise.resolve();
            }
            var data = this.generate_mandiri_ecr_message(paymentLine.payment_method.mandiri_trans_type, paymentLine);            
            this.send_data_to_web_socket(data);
            this.set_payment_line_status(paymentStatus.WAITING);
            return this.start_get_status_polling();
        },

        close: function () {
            this._super.apply(this, arguments);
        },

        _reset_state: function () {
          this.was_cancelled = false;
          this.remaining_polls = 4;
          clearTimeout(this.polling);
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

    return PaymentMandiriEcr
});