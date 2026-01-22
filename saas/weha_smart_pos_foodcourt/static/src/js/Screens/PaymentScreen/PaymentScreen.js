odoo.define('weha_smart_pos_foodcourt.PaymentScreen', function(require) {

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const { posbus } = require('point_of_sale.utils');
    const { useState } = owl.hooks;
    const NumberBuffer = require('point_of_sale.NumberBuffer');

    const DepositPaymentScreen = PaymentScreen =>
        class extends PaymentScreen {
            constructor(){
                super(...arguments);
                this.state = useState({ remaining_deposit_amount: false});
            }
            get_client_remaining_amount(){
                return this.env.pos.get_client() ? this.env.pos.get_client().remaining_deposit_amount : null;
            }
            deletePaymentLine(event){
                const { cid } = event.detail;
                const line = this.paymentLines.find((line) => line.cid === cid);
                if (['waiting', 'waitingCard', 'timeout'].includes(line.get_payment_status())) {
                    line.payment_method.payment_terminal.send_payment_cancel(this.currentOrder, cid);
                }
                this.currentOrder.remove_paymentline(line);
                if(line.payment_method.allow_for_wallet){
                    this.currentOrder.set_to_deposit(!this.currentOrder.is_to_deposit());
                    this.state.remaining_deposit_amount += line.amount;
                }
                NumberBuffer.reset();
                this.render();
            }
            async createPaymentLine(){
                let self = this
                let order = self.currentOrder;
                if(order.is_to_wallet()){
                    return;
                }
                let client = order.get_client();
                let lines = order.get_paymentlines();
                for ( var i = 0; i < lines.length; i++ ){
                    if(lines[i].payment_method.allow_for_deposit){
                        self.deletePaymentLine({ detail: { cid: lines[i].cid } });
                    }
                }
                let amount = client.remaining_deposit_amount >= order.get_due() ? order.get_due() : client.remaining_deposit_amount;
                if(client.remaining_deposit_amount == 0 || client.remaining_deposit_amount < 0){
                    return
                }
                const { confirmed, payload: redeemAmount } = await self.showPopup('TopupDepositPopup',{
                    customer: client.name || false,
                    rechargeAmount: amount,
                    flag : 'from_payment',
                    wallet_bal : client.remaining_deposit_amount,
                    title: self.env._t('Redeem Deposit'),
                });
                if (confirmed){
                    order.set_used_amount_from_wallet(Math.abs(redeemAmount));
                    order.set_type_for_wallet('change');
                    var payment_method = _.find(self.env.pos.payment_methods, function(cashregister){
                        return cashregister.id === self.env.pos.config.deposit_payment_method_id[0] ? cashregister : false;
                    });
                    if(payment_method){
                        order.add_paymentline(payment_method);
                        order.selected_paymentline.set_amount(Number(redeemAmount));
                        order.set_to_deposit(!order.is_to_deposit());
                        self.env.pos.load_new_partners();
                        self.state.remaining_deposit_amount -= order.selected_paymentline.amount;
                        self.render();
                        return
                    }
                }
            }
            async payment_back(){
                if(this.env.pos.get_order().get_orderlines().length != 0){
                    if(this.env.pos.config.deposit_product && this.env.pos.get_order().get_orderlines()[0].product.id == this.env.pos.config.deposit_product[0]){
                        const { confirmed } = await this.showPopup('ConfirmPopup', {
                            title: this.env._t('You do not go back'),
                            body: this.env._t(
                                'Would you like to discart this order?'
                            ),
                        });
                        if (confirmed){
                            this.env.pos.get_order().destroy({ reason: 'abandon' });
                            posbus.trigger('order-deleted');
                            this.showScreen('ProductScreen')
                        }
                    }else{
                        this.showScreen('ProductScreen')
                    }
                }else{
                    this.showScreen('ProductScreen')
                }
            }
            async validateOrder(isForceValidate){
                if(this.currentOrder.get_client()){
                    if(this.currentOrder.get_change() && this.env.pos.config.enable_wallet
                    && !this.currentOrder.get_client().add_change_deposit && this.currentOrder.get_type_for_wallet() != 'recharge'){
                        const {confirmed, skip, getPayload} = await this.showPopup('PaymentDepositPopup', {
                            title: this.env._t('Add to Deposit'),
                            change: this.env.pos.format_currency(this.currentOrder.get_change()),
                            nextScreen: this.nextScreen,
                            order: this,
                        });
                        if (confirmed){
                            return super.validateOrder();
                        }else if(skip){
                            return super.validateOrder();
                        }
                    }else if(this.currentOrder.get_client().add_change_deposit){
                         this.currentOrder.set_type_for_deposit('change');
                         this.currentOrder.set_change_amount_for_wallet(this.currentOrder.get_change());
                         return super.validateOrder();
                    }
                }else{
                    return super.validateOrder();
                }
                return super.validateOrder();
            }
        };

    Registries.Component.extend(PaymentScreen, DepositPaymentScreen);

    return PaymentScreen;
});
