odoo.define('pos_cash_opening_zero.CashMovePopup', function (require) {
    "use strict";    
    const { useState, useRef, onMounted } = owl;
    const { parse } = require('web.field_utils');
    const CashMovePopup = require('point_of_sale.CashMovePopup');
    const Registries = require("point_of_sale.Registries");

    const PosCashOpeningZeroCashMovePopup = (CashMovePopup) =>
        class extends CashMovePopup{
            setup() {
                super.setup();
                this.manualInputCashCount = null;                
                this.state.notes = "";
                this.state.cashInOut = 0;
                this.state.displayMoneyDetailsPopup = false;
                this.state.moneyDetailsJson = [];
                this.state.inputAmount = '';            
                this.inputAmountRef = useRef('input-amount-ref');
                
                onMounted(() => {
                    if (this.inputAmountRef.el) {
                        this.inputAmountRef.el.disabled = true;
                        // Limit input to numbers and decimal point only
                        this.inputAmountRef.el.addEventListener('input', (e) => {
                            e.target.value = e.target.value.replace(/[^0-9.]/g, '');
                            // Prevent multiple decimal points
                            const parts = e.target.value.split('.');
                            if (parts.length > 2) {
                                e.target.value = parts[0] + '.' + parts.slice(1).join('');
                            }
                            // Prevent starting with zero unless it's a decimal (0.)
                            if (e.target.value.length > 1 && e.target.value[0] === '0' && e.target.value[1] !== '.') {
                                e.target.value = e.target.value.substring(1);
                            }
                            // Update the state with the validated value
                            this.state.inputAmount = e.target.value;
                            this.handleInputChange();
                        });
                    }
                });                             
            }
            
            async confirm() {
                if (this.state.inputAmount === '') {                    
                    return;
                }   

                if (parse.float(this.state.inputAmount) === 0) {                    
                    return;
                }

                if (this.state.inputType === 'out'){
                    this.state.inputAmount = this.state.inputAmount.charAt(0) === '-' ? this.state.inputAmount : `-${this.state.inputAmount}`;
                }                                         
                return super.confirm();
            }

            openDetailsPopup() {
                this.state.cashInOut = 0;
                this.state.notes = "";
                this.state.displayMoneyDetailsPopup = true;
            }

            closeDetailsPopup() {
                this.state.displayMoneyDetailsPopup = false;
            }

            updateCashOpening({ total, moneyDetailsNotes, moneyDetails }) {
                this.inputAmountRef.el.value = `-${total}`;
                this.state.cashInOut = total;

                this.state.inputAmount = total * -1;
                
                if (this.state.inputAmount < 0) {
                    this.state.inputAmount = `-${this.state.inputAmount * -1}`;
                }else{
                    this.state.inputAmount = `${this.state.inputAmount}`
                }
                this.state.parsedAmount = parse.float(this.state.inputAmount);
                if (moneyDetailsNotes) {
                    this.state.inputReason = moneyDetailsNotes;
                }
                this.manualInputCashCount = false;
                console.log('moneyDetails');
                console.log(moneyDetails)
                this.env.pos.bills.forEach(bill => {
                    if (moneyDetails[bill.value]) {
                        this.state.moneyDetailsJson.push({quantity: moneyDetails[bill.value], value: bill.value, fmtAmount: this.env.pos.format_currency(bill.value), total: bill.value * moneyDetails[bill.value], fmtTotal:this.env.pos.format_currency(bill.value * moneyDetails[bill.value])});                        
                    }else{
                        this.state.moneyDetailsJson.push({quantity: 0, value: bill.value, fmtAmount: this.env.pos.format_currency(bill.value), total: 0, fmtTotal:this.env.pos.format_currency(0) });                        
                    }
                })
                this.closeDetailsPopup();
            } 

            onClickButton(type) {               
                this.state.inputAmount = '';
                this.state.inputType = type;
                this.state.inputHasError = false;
                if (this.inputAmountRef.el) {
                    this.inputAmountRef.el.disabled = false;
                    this.inputAmountRef.el.focus();
                    this.inputAmountRef.el.value = '';
                }               
            }

            getPayload() {
                var result = super.getPayload();
                result.details = this.state.moneyDetailsJson;                
                return result;
            }
            
            handleInputChange() {
                // if (!this.state.inputAmount || isNaN(this.state.inputAmount)) {
                //     this.state.inputHasError = true;
                //     this.state.parsedAmount = 0;
                //     return;
                // }
                if (this.state.inputType === 'in') {
                    this.state.parsedAmount = parse.float(this.state.inputAmount);
                }
                if (this.state.inputType === 'out') {
                    // this.state.parsedAmount = parse.float(`-${this.state.inputAmount}`);
                    this.state.parsedAmount = parse.float(this.state.inputAmount);
                }
            }
        }
    
    Registries.Component.extend(CashMovePopup, PosCashOpeningZeroCashMovePopup);

});