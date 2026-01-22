odoo.define('weha_smart_pos_aeon_prima.PaymentPrima', function(require){
    
  const core = require('web.core')
  var rpc = require('web.rpc');
  const PaymentInterface = require('point_of_sale.PaymentInterface')
  const { Gui } = require('point_of_sale.Gui')

  const paymentStatus = {
      PENDING: 'pending',
      RETRY: 'retry',
      WAITING: 'waiting',
      FORCE_DONE: 'force_done',
      WAITING_PRIMA_QRIS: 'waiting_prima_qris',
      CHECK_QRIS: 'check_qris'
  }

  const _t = core._t

  const PaymentPrima = PaymentInterface.extend({
      
      init: function (pos, payment_method) {
        this._super(...arguments);
        this.successEcr = false;
        this.waitingEcr = false;
        this.was_cancelled = false;
        this.pooling_count = 0;
        this.transaction_type = "qris"; // qrid and refund
      },

      set_payment_line_status: function(status){
        const order = this.pos.get_order()
        let paymentLine = order.selected_paymentline;
        paymentLine.set_payment_status(status)
      },

      set_payment_line_value_for_prima_qris: function(result_data){
        const order = this.pos.get_order();
        let paymentLine = order.selected_paymentline;
        paymentLine.set_is_prima(true);
        paymentLine.set_partner_reference_no(result_data.partnerReferenceNo);        
        paymentLine.set_external_id(result_data.xExternalId);
        paymentLine.set_transaction_hash(result_data.additionalInfo.transactionHash); 
        paymentLine.set_transaction_date(result_data.xTimestamp);        
      },

      set_payment_line_value_for_prima_qris_status: function(result_data){
        const order = this.pos.get_order();
        let paymentLine = order.selected_paymentline;
        console.log('set_payment_line_value_for_prima_qris_status');
        console.log(result_data);
        paymentLine.set_reference_no(result_data.originalReferenceNo);        
        paymentLine.set_merchant_id(result_data.additionalInfo.merchantData.merchantId);
        paymentLine.set_terminal_id(result_data.additionalInfo.merchantData.terminalId);
        paymentLine.set_pan(result_data.additionalInfo.issuerData.cPan);
        paymentLine.set_service_code(result_data.serviceCode);
        paymentLine.set_invoice_number(result_data.additionalInfo.invoiceNumber);
        paymentLine.set_transaction_id(result_data.additionalInfo.transactionId);
      },

      set_payment_line_value_for_prima_qris_refund: function(result_data){
        console.log('set_payment_line_value_for_prima_qris_refund')
        const order = this.pos.get_order();
        let paymentLine = order.selected_paymentline;
        paymentLine.set_refund_reference_no(result_data.referenceNo);
        paymentLine.set_refund_time(result_data.refundTime);
      },

      send_payment_request: async function() {
          await this._super.apply(this, arguments);                 
          this._reset_state();
          return this._prima_pay();
      },

      check_payment_prima_qris: function(){
        return this._prima_check();
      },
      
      send_payment_cancel: function (order, cid) {
          this._super.apply(this, arguments);
          //this.pos_interface_conn.close();
          return Promise.resolve();
      },

      close: function () {
          this.was_cancelled = true;
          console.log('was cancelled');
          this._super.apply(this, arguments);
      },      

      _reset_state: function () {
        this.was_cancelled = false
        this.last_diagnosis_service_id = false
        this.remaining_polls = 100
        clearTimeout(this.polling)
      }, 

      _handle_odoo_connection_failure: function (data) {
        // handle timeout
        const order = this.pos.get_order();
        let paymentLine = order.selected_paymentline;
        if (paymentLine) {
          paymentLine.set_payment_status(paymentStatus.RETRY)
        }  
        this._show_error(_t('Could not connect to the Odoo server, please check your internet connection and try again.'))
        return Promise.reject(data) // prevent subsequent onFullFilled's from being called
      }, 

      _prima_pay: async function () {          
          const self = this;          
          // Check Terminal ID
          if(!this.pos.config.prima_terminal_id){
            this._showError(
              _t('Cannot process transaction without prima terminal id information.')
            )
            return Promise.resolve();  
          }

          const order = this.pos.get_order();
          let paymentLine = order.selected_paymentline;          
          if (paymentLine && paymentLine.amount <= 0) {
            if (!order.get_is_void() && !order.get_is_refund()){              
              this._showError(
                _t('Cannot process transaction with zero or negative amount.')
              )
              return Promise.resolve();  
            }
            console.log('this is void or refund order')
          }                         

          const receipt_data = order.export_for_printing()
          receipt_data.amount = paymentLine.amount
          receipt_data.terminal_id = this.pos.config.prima_terminal_id
          
          if (order.get_is_void() === true || order.get_is_refund() === true){ 
            this.transaction_type = 'refund'
          }else{
            this.transaction_type = 'qris'
          }

          return this._call_prima(order,paymentLine).then(function (data) {
            return self._prima_handle_response(data)
          })
      },     

      _call_prima: function (order, paymentLine) {
        var self = this;
        if(this.transaction_type === 'qris'){
          return rpc.query({
            model: "pos.payment",
            method: "request_prima_qris",
            args: [order.name, paymentLine.amount, order.name, this.pos.config.prima_merchant_id, this.pos.config.prima_terminal_id]
          },{         
            timeout: 10000,
            shadow: true
          }).catch(
            this._handle_odoo_connection_failure.bind(this)
          );
        }else{
          return rpc.query({
            model: "pos.payment",
            method: "request_prima_qris_status",          
            args: [paymentLine.get_partner_reference_no(), paymentLine.get_external_id(), paymentLine.get_transaction_date(), paymentLine.get_transaction_hash(), this.pos.config.prima_merchant_id]
          },{         
            timeout: 10000,
            shadow: true
          }).catch(
            this._handle_odoo_connection_failure.bind(this)
          );
        }              
      },

      _prima_handle_response: function (result) {
          const self = this
          const order = this.pos.get_order();
          const paymentLine = order.selected_paymentline;
          const result_json = JSON.parse(result);
          if(this.transaction_type === 'qris'){
            if(result_json.error == false){
              const result_data = result_json.data;
              self.set_payment_line_value_for_prima_qris(result_data)                      
              self.pos.send_prima_qrcode_to_customer_facing_display(result_data.qrContent);
              self.set_payment_line_status(paymentStatus.WAITING);
              // Gui.showPopup('PrimaWaitingPopup', {});                                  
            }else{
              self.set_payment_line_status(paymentStatus.RETRY);
              self._showError(
                _t(result_json.data.responseCode + " : " + result_json.data.responseMessage)
              )
            }
          }                
          return this.start_get_status_polling()        
      },
      _prima_check: async function () {
        console.log('_prima_check');
        const self = this;
          const order = this.pos.get_order();
          let paymentLine = order.selected_paymentline;
          if (paymentLine && paymentLine.amount <= 0) {
            this._showError(
              _t('Cannot process transaction with zero or negative amount.')
            )
            return Promise.resolve();
          }                    
          this._request_prima_qris_status(order, paymentLine);                
          return this.start_get_status_polling();
      },
      _request_prima_qris: function (order, paymentLine) {        
        var self = this;
        return rpc.query({
          model: "pos.payment",
          method: "request_prima_qris",
          args: [order.name, paymentLine.amount, order.name, this.pos.config.prima_merchant_id, this.pos.config.prima_terminal_id]
        },{async:false}).then(function(result){
          const result_json = JSON.parse(result);
          if(result_json.error == false){
            self.successEcr = false;            
            self.set_payment_line_status(paymentStatus.WAITING_PRIMA_QRIS);            
            const result_data = result_json.data;
            console.log(result_data);
            self.set_payment_line_value_for_prima_qris(result_data)                      
            self.pos.send_prima_qrcode_to_customer_facing_display(result_data.qrContent);                     
          }else{
            self.successEcr = false;            
            self.set_payment_line_status(paymentStatus.RETRY);
            self._showError(
              _t(result_json.data.responseCode + " : " + result_json.data.responseMessage)
            )
          }
        });
      },
      _request_prima_qris_status: async function (order, paymentLine) {        
        var self = this;
        await rpc.query({
          model: "pos.payment",
          method: "request_prima_qris_status",          
          args: [paymentLine.get_partner_reference_no(), paymentLine.get_external_id(), paymentLine.get_transaction_date(), paymentLine.get_transaction_hash(), this.pos.config.prima_merchant_id]
        },{async: false}).then(function(result){
          const result_json = JSON.parse(result);
          const result_data = result_json.data;
          // self.set_payment_line_status("waitingCard");
          console.log(result_json.data);           
          if(result_json.error == false){                                    
            self.set_payment_line_value_for_prima_qris_status(result_data);
            self.successEcr = true;               
          }else{
            self.successEcr = false;
            self.set_payment_line_status(paymentStatus.WAITING_PRIMA_QRIS);
            self._showError(
              _t(result_json.data.responseCode + " : " + result_json.data.transactionStatusDesc)
            )
          }
        });
      },
      _request_prima_qris_refund: async function (order, paymentLine) { 
        var self = this;
        await rpc.query({
          model: "pos.payment",
          method: "request_prima_qris_refund",
          // partnerRefundNo, originalPartnerReferenceNo, originalReferenceNo, originalExternalId, reason        
          // token, partnerRefundNo, partnerReferenceNo, referenceNo, externalId,  transactionDate, amount, reason
          args: [
            order.get_name(), 
            paymentLine.get_partner_reference_no(), 
            paymentLine.get_reference_no(), 
            paymentLine.get_external_id(), 
            paymentLine.get_transaction_date(), 
            -1 * paymentLine.amount,
            "",
            this.pos.config.prima_merchant_id]
        },{async: false}).then(function(result){
          const result_json = JSON.parse(result);
          const result_data = result_json.data;
          console.log(result_json.data);           
          if(result_json.error == false){                        
            // Complete payment line data           
            self.set_payment_line_value_for_prima_qris_refund(result_data);
            self.successEcr = true;               
          }else{
            self.successEcr = false;
            self.set_payment_line_status(paymentStatus.RETRY);
            self._showError(
              _t(result_data.responseCode + " - " + result_data.responseMessage)
            )
          }
        });
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

      const order = this.pos.get_order();
      let paymentLine = order.selected_paymentline;

      // If the payment line dont have xendit invoice then stop polling retry.
      // if (!paymentLine || paymentLine.getXenditInvoiceId() == null) {
      //   resolve(false)
      //   return Promise.resolve()
      // }

      // const data = {
      //   transaction_hash: paymentLine.get_transaction_hash(),
      // }

      return rpc.query({
        model: 'pos.payment',
        method: 'get_latest_prima_payment_status',
        args: [paymentLine.get_transaction_hash()]
      }, {
        timeout: 5000,
        shadow: true
      }).catch(function (data) {
        reject()
        return self._handle_odoo_connection_failure(data)
      }).then(function (result) {      
        const result_json = JSON.parse(result);
        console.log(result_json);
        const result_data = result_json.data;
        console.log(result_data);
        if(!result_json.error){
          // self._update_payment_status(invoice, resolve, reject)
          console.log("Get Status");              
          if(result_json.error == false){                                    
            self.set_payment_line_value_for_prima_qris_status(result_data);   
            resolve();        
          }else{
            self.set_payment_line_status(paymentStatus.WAITING_PRIMA_QRIS);
            self._showError(
              _t(result_json.data.responseCode + " : " + result_json.data.transactionStatusDesc)
            )
          }
        }else{
          self.remaining_polls -= 1;
          console.log(self.remaining_polls)
          if(self.remaining_polls == 0){
            self._reset_state();
            paymentLine.set_payment_status(paymentStatus.WAITING_PRIMA_QRIS)
            reject()
          }
        }        
      })
    },

    _showError: function (msg, title) {
      if (!title) {
          title =  _t('Prima QRIS Error');
      }
      Gui.showPopup('ErrorPopup',{
          'title': title,
          'body': msg,
      });
  },
  });

  return PaymentPrima    
});
