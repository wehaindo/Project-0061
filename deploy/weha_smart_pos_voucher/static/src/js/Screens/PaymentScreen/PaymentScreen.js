odoo.define('weha_smart_pos_voucher.PaymentScreen', function (require) {
	'use strict';

	const PaymentScreen = require('point_of_sale.PaymentScreen');
	const Registries = require('point_of_sale.Registries');
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
			get check_Paymentline(){
				var flag = true;
				_.each(this.env.pos.get_order().get_paymentlines(), function(payment_method){
					if(payment_method.payment_method.allow_for_gift_voucher){
						flag=false;
					}
				})
				return flag;
			}
			async useGiftVoucher()  {
				var self = this;
				var order = self.env.pos.get_order();
				var client = order.get_partner();
				var vouchers = order.get_redeem_giftvoucher();

				const {confirmed, payload: giftVoucher} = await self.showPopup('giftVoucherRedeemPopup', {
					title: self.env._t('Gift Voucher'),
				});

				if (confirmed){
					var code = giftVoucher.number;
					var today = moment().locale('en').format('YYYY-MM-DD');
					if(code){
						var params = {
							model: 'aspl.gift.voucher',
							method: 'search_read',
							domain: [['voucher_code', '=', code]],
						}
						var result = await rpc.query(params, {async: false}).then(function(res){
							return res;
						});
						if(result && result.length > 0) {
                            var expiry_date = moment(result[0]['expiry_date']).format('YYYY-MM-DD');
                            var order_total_without_tax = order.get_total_without_tax();
                            if(result[0]['expiry_date'] && today > expiry_date){
                               return;
                            }else if(!result[0]['is_active']){
                                return;
                            }else if(result[0]['minimum_purchase'] && result[0]['minimum_purchase'] > 0 &&
                                                        order_total_without_tax < result[0]['minimum_purchase']){
                                return;
                            }else if(result[0]['voucher_amount'] > order.get_due()) {
                                return;
                            }else{
                                var redeem_amount = Number(result[0]['voucher_amount']);
                                var voucher_id = result[0]['id'];
                                if(redeem_amount > 0){
                                    if(self.env.pos.config.gift_voucher_payment_method[0]){
                                        var cashregisters = null;
                                        for ( var j = 0; j <  self.env.pos.payment_methods.length; j++ ) {
                                            if( self.env.pos.payment_methods[j].id === self.env.pos.config.gift_voucher_payment_method[0]){
                                                cashregisters = self.env.pos.payment_methods[j];
                                            }
                                        }
                                    }
                                    if (cashregisters){
                                        if (self.env.pos.get_order().get_partner()){
                                            if(!vouchers){
                                                self.check_redemption_customer(voucher_id).then(function(redeem_count){
                                                    if(result[0]['redemption_customer'] != 0 && redeem_count == 0 ||
                                                                        redeem_count < result[0]['redemption_customer']){
                                                        order.add_paymentline(cashregisters);
                                                        order.selected_paymentline.set_amount( Math.max(redeem_amount),0 );
                                                        order.set_redeem_giftvoucher(result[0]);
                                                    }
                                                });
                                            }else{
                                                if(result[0]['voucher_code'] == code){
                                                    var voucher_use = _.countBy(vouchers, 'voucher_code');
                                                    if (voucher_use[code]){
                                                        if(result[0]['redemption_order'] > voucher_use[code]){
                                                            self.check_redemption_customer(voucher_id).then(function(redeem_count){
                                                                if (result[0]['redemption_order'] != 0 && redeem_count == 0
                                                                        || redeem_count < result[0]['redemption_customer']){
                                                                    order.add_paymentline(cashregisters);
                                                                    order.selected_paymentline.set_amount( Math.max(redeem_amount),0 );
                                                                    order.set_redeem_giftvoucher(result[0]);

                                                                }
                                                            });
                                                        }
                                                    } else{
                                                        self.check_redemption_customer(voucher_id).then(function(redeem_count){
                                                            if (result[0]['redemption_customer'] != 0 && redeem_count == 0 || redeem_count < result[0]['redemption_customer']){
                                                                order.add_paymentline(cashregisters);
                                                                order.selected_paymentline.set_amount( Math.max(redeem_amount),0 );
                                                                order.set_redeem_giftvoucher(result[0]);
                                                            }
                                                        });
                                                    }
                                                }
                                            }
                                        }else{
                                            self.showNotification("Select Customer First!!",4000);
                                        }
                                    }
                                    self.trigger('close-popup');
                                }
                            }
						}
					}
				}
			}
			check_redemption_customer(voucher_id){
				var self = this;
				var order = self.env.pos.get_order();
				var domain = [['voucher_id', '=', voucher_id]];
				if(order.get_partner()){
					domain.push(['customer_id', '=', order.get_partner().id])
				}
				var params = {
					model: 'aspl.gift.voucher.redeem',
					method: 'search_count',
					args: [domain],
				}
				return rpc.query(params, {async: false})
			}
		};

	Registries.Component.extend(PaymentScreen, PaymentScreenInherit);

	return PaymentScreenInherit;
});
