odoo.define('weha_smart_pos_aeon_pms.PaymentScreen', function (require) {
	'use strict';

	const PaymentScreen = require('point_of_sale.PaymentScreen');
	const Registries = require('point_of_sale.Registries');
	const NumberBuffer = require('point_of_sale.NumberBuffer');
	const { useListener } = require("@web/core/utils/hooks");
	const { posbus } = require('point_of_sale.utils');
	var core = require('web.core');
	var _t = core._t;
	var rpc = require('web.rpc');

	const PaymentScreenInherit = (PaymentScreen) =>
		class extends PaymentScreen {
			setup() {
                super.setup();
            }
			
			check_paymentline(){
				var line = null;
				_.each(this.env.pos.get_order().get_paymentlines(), function(paymentline){
					if(paymentline.payment_method.allow_pms_voucher){
						line=paymentline;
					}
				})
				return line;
			}		

			async usePmsVoucher()  {
				var self = this;
				var order = self.env.pos.get_order();
				var redeem_amount = 100000;
				const {confirmed, payload: voucherInfo} = await self.showPopup('PmsVoucherPopup', {
					title: self.env._t('PMS  Voucher'),
				});
				console.log(voucherInfo);
				var stamp = moment().locale('en').format('DD-MM-YYYY HH:mm:ss');
				if (confirmed){
					var data = {
						"coupon_no":voucherInfo['number'],
						"type":1,
						"card_no": order.get_card_no(),
						"stamp":stamp,
						"pos_code":"004",
						"serial_number":"0040054",
						"merchant_id":"00",
						"ou_id":"01",
						"mb_id":"01004",
						"counter_code":"01004"
					}
					console.log(data);
		
					await this.rpc({
						model: 'res.partner',
						method: 'pms_process_use_coupon',
						args: [data,data],
					}).then(function (result) {
						console.log(result);
						var result_json = JSON.parse(result);
						if(result_json.err == false){                 
							var result_data = result_json.data[0];
							if(result_data["ERROR_CODE"] == "0"){
								console.log("Success");
								console.log(self.env.pos.config.pms_voucher_payment_method);
								if(self.env.pos.config.pms_voucher_payment_method[0]){
									var cashregisters = null;
									for ( var j = 0; j <  self.env.pos.payment_methods.length; j++ ) {
										if( self.env.pos.payment_methods[j].id === self.env.pos.config.pms_voucher_payment_method[0]){
											cashregisters = self.env.pos.payment_methods[j];
										}
									}
								}
								if(cashregisters){
									var paymentline = self.check_paymentline();
									if(paymentline !== null){
										order.select_paymentline(paymentline);
									}else{
										order.add_paymentline(cashregisters);
									}
									console.log(voucherInfo['amount']);
									

									// order.selected_paymentline.set_voucher_no(voucherInfo['number'])
									console.log("Selected Payment Line");
									console.log(order.selected_paymentline);
									var newvoucherline = order.selected_paymentline.add_voucher_line({});
									newvoucherline.set_voucher_full(voucherInfo['full']);
									newvoucherline.set_voucher_no(voucherInfo['number']);
									newvoucherline.set_voucher_amount(Math.max(voucherInfo['amount']),0 );
									order.selected_paymentline.set_amount(order.selected_paymentline.get_total_voucher());										
								}else{
									self.showPopup('ErrorPopup', {
										title: _t('Payment Method Error'),
										body: _t('Please defind payment method for voucher!')
									});
								}
							}else{
								console.log("Failed : " + result_data["ERROR_CODE"])
								self.showPopup('ErrorPopup', {
									title: _t('Payment Method Error'),
									body: _t("Error " + result_data["ERROR_CODE"] + " -> " + result_data["ERROR_MSG"])
								});
							}
						}else{
							console.log("Error");
							self.showPopup('ErrorPopup', {
								title: _t('Payment Method Error'),
								body: _t("Error " + result_data["ERROR_CODE"] + " -> " + result_data["ERROR_MSG"])
							});
						}
					}); 
				}
            }

			async deletePaymentLine(event) {
				var self = this;
				const { cid } = event.detail;
				const line = this.paymentLines.find((line) => line.cid === cid);
	
				// If a paymentline with a payment terminal linked to
				// it is removed, the terminal should get a cancel
				// request.
				if (['waiting', 'waitingCard', 'timeout'].includes(line.get_payment_status())) {
					line.set_payment_status('waitingCancel');
					line.payment_method.payment_terminal.send_payment_cancel(this.currentOrder, cid).then(function() {
						self.currentOrder.remove_paymentline(line);
						NumberBuffer.reset();
						self.render(true);
					})
				}
				else if (line.get_payment_status() !== 'waitingCancel') {
					if(line.payment_method.allow_pms_voucher){
						var voucherlines = line.get_voucherlines();
						var html_body = "";					
						for ( var j = 0; j <  voucherlines.length; j++ ) {
							html_body += voucherlines[j].get_voucher_no() + ","
						}
						var vouchers = voucherlines.map(voucher => {
							return voucher.get_voucher_full();
						})
						console.log("vouchers");
						console.log(vouchers);
						const { confirmed } = await this.showPopup('ConfirmPopup', {
							title: this.env._t('Delete PMS Voucher'),
							body: this.env._t(
								"This payment  with " + voucherlines.length.toString() +
								" vouchers (" + html_body + "), " +
								'Do you want to delete this payment?'
							),
						});
						if (confirmed) {
							// NOTE: Not yet sure if this should be awaited or not.
							// If awaited, some operations like changing screen
							// might not work.							
							for ( var j = 0; j <  voucherlines.length; j++ ) {
								var stamp = moment().locale('en').format('DD-MM-YYYY HH:mm:ss');
								var data = {
									"coupon_no": voucherlines[j].get_voucher_no(),
									"type":0,
									"card_no": self.currentOrder.get_card_no(),
									"stamp":stamp,
									"pos_code":"004",
									"serial_number":"0040054",
									"merchant_id":"00",
									"ou_id":"01",
									"mb_id":"01004",
									"counter_code":"01004"
								}
								console.log(data)
								await this.rpc({
									model: 'res.partner',
									method: 'pms_process_use_coupon',
									args: [data,data],
								}).then(function (result) {
									
								});	
							}
							this.currentOrder.remove_paymentline(line);
							NumberBuffer.reset();
							this.render(true);
						}
					}else{
						console.log(line.payment_method);
						this.currentOrder.remove_paymentline(line);
						NumberBuffer.reset();
						this.render(true);
					}
				}
			}

			_updateSelectedPaymentline() {
				if (this.paymentLines.every((line) => line.paid)) {
					this.currentOrder.add_paymentline(this.payment_methods_from_config[0]);
				}
				if (!this.selectedPaymentLine) return; // do nothing if no selected payment line
				// disable changing amount on paymentlines with running or done payments on a payment terminal
				const payment_terminal = this.selectedPaymentLine.payment_method.payment_terminal;
				if (
					payment_terminal &&
					!['pending', 'retry'].includes(this.selectedPaymentLine.get_payment_status())
				) {
					return;
				}
				if (NumberBuffer.get() === null) {
					this.deletePaymentLine({ detail: { cid: this.selectedPaymentLine.cid } });
				} else {
					if(!this.selectedPaymentLine.payment_method.allow_for_gift_voucher){
						this.selectedPaymentLine.set_amount(NumberBuffer.getFloat());
					}
				}
			}
		};

	Registries.Component.extend(PaymentScreen, PaymentScreenInherit);

	return PaymentScreenInherit;
});
