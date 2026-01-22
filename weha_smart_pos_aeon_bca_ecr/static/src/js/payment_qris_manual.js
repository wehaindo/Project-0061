odoo.define('weha_smart_pos_aeon_bca_ecr.PaymentQrisManual', function(require){
    
    const core = require('web.core')
    const rpc = require('web.rpc')
    const PaymentInterface = require('point_of_sale.PaymentInterface')
    const { Gui } = require('point_of_sale.Gui')
  
    const paymentStatus = {
        PENDING: 'pending',
        RETRY: 'retry',
        WAITING: 'waiting',
        FORCE_DONE: 'force_done',
        WAITING_INPUT: 'waiting_manual_input'
    }

    const _t = core._t

    const PaymentQrisManual = PaymentInterface.extend({
        
        init: function (pos, payment_method) {
          this._super(...arguments);
          this.successInput = false;
          this.waitingInput = false;
        },

        check_qris_manual: function(){
          return this._qris_manual_check();
        },

        _qris_manual_check: function(){
          console.log('_qris_manual_check');
          const self = this;
          const order = this.pos.get_order();
          let paymentLine = order.selected_paymentline;
          if (paymentLine && paymentLine.amount <= 0) {
            this._show_error(
              _t('Cannot process transaction with zero or negative amount.')
            )
            return Promise.resolve();
          }
          this.set_payment_line_status(paymentStatus.WAITING_INPUT);    
          return Promise.resolve();
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

        console.log('successInput 1');
        console.log(this.successInput);

        if(this.successInput){
          console.log("Success Payment 2");
          this.successInput = false;
          console.log('successECR 2');
          console.log(this.successInput);
          resolve(true)
          return Promise.resolve();
        }

    },  

    });

    return PaymentQrisManual    
});
