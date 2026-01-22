odoo.define('aspl_pos_wallet.AddMoneyToWalletPopup', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    class AddMoneyToWalletPopup extends AbstractAwaitablePopup {
        constructor(){
            super(...arguments);
            this.state = useState({ customer: this.props.customer, rechargeAmount: this.props.rechargeAmount,
                                    message: '', showMsg : false});
            this.inputRef = useRef('input');
        }
        mounted(){
            this.inputRef.el.focus();
        }
        async confirm(){
            if(this.props.flag == 'from_payment'){
                if(this.state.rechargeAmount > this.env.pos.get_order().get_due()){
                    this.state.showMsg = true;
                    this.state.message = 'You are not allow to use wallet amount More then remaining amount !!!';
                    return
                }else if(this.state.rechargeAmount > this.env.pos.get_order().get_client().remaining_wallet_amount){
                    this.state.showMsg = true;
                    this.state.message = 'Not Enough Balance In Wallet !!!';
                    return
                }
            }
            this.props.resolve({ confirmed: true, payload: await this.getPayload()});
            this.trigger('close-popup');
        }
        getPayload(){
            return this.state.rechargeAmount;
        }
        onInputKeyDown(e) {
            if(e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57) && (e.which < 96 || e.which > 105)) {
                e.preventDefault();
            }
        }
    }
    AddMoneyToWalletPopup.template = 'AddMoneyToWalletPopup';

    AddMoneyToWalletPopup.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: '',
        body: '',
        rechargeAmount: '',
    };

    Registries.Component.add(AddMoneyToWalletPopup);

    return AddMoneyToWalletPopup;
});
