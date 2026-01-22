odoo.define('xendit_qris.payment', function(require){
    'use strict'

    const core = require('web.core')
    const rpc = require('web.rpc')
    const PaymentInterface = require('point_of_sale.PaymentInterface')
    const { Gui } = require('point_of_sale.Gui')

    const paymentStatus = {
        PENDING: 'pending',
        RETRY: 'retry',
        WAITING: 'waiting',
        FORCE_DONE: 'force_done'
    }

    const _t = core._t

    const PaymentXenditQris = PaymentInterface.extend({
        send_payment_request: function () {
            this._super.apply(this, arguments)
            this._reset_state()
            return this._xendit_qris_pay()
          },
    
        get_selected_payment: function () {
            const paymentLine = this.pos.get_order().selected_paymentline
            if (paymentLine && paymentLine.payment_method.use_payment_terminal === 'xendit_qris') {
              return paymentLine
            }
            return false
        },

        _xendit_qris_pay: function () {
            const self = this
      
            const order = this.pos.get_order()
            const paymentLine = this.get_selected_payment()
            if (paymentLine && paymentLine.amount <= 0) {
              this._show_error(
                _t('Cannot process transaction with zero or negative amount.')
              )
              return Promise.resolve()
            }
      
            const receipt_data = order.export_for_printing()
            receipt_data.amount = paymentLine.amount
            receipt_data.terminal_id = paymentLine.payment_method.xendit_pos_terminal_identifier
      
            return this._call_xendit(receipt_data).then(function (data) {
              return self._xendit_handle_response(data)
            })
          },
    })  

    
});