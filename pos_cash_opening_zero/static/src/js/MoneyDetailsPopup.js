odoo.define('pos_cash_opening_zero.MoneyDetailsgPopup', function (require) {
    "use strict";    
    const { useState, useRef, onMounted } = owl;
    const MoneyDetailsgPopup = require('point_of_sale.MoneyDetailsPopup');
    const Registries = require("point_of_sale.Registries")

    const MoneyDetailsgPopupCashOpeningZero = (MoneyDetailsgPopup) =>
        class extends MoneyDetailsgPopup{
            setup() {
                super.setup()
                this.state = useState({
                    moneyDetails: Object.fromEntries(this.env.pos.bills.map(bill => ([bill.value, 0]))),
                    total: 0,
                });
            }

            get firstHalfMoneyDetails() {
                const moneyDetailsKeys = Object.keys(this.state.moneyDetails).sort((a, b) => a - b);
                return moneyDetailsKeys
            }
            get lastHalfMoneyDetails() {                
                return {}
            }

            clearMoneyDetails() {
                this.state.moneyDetails = {};
                this.state.total = 0;
            }

            getTotalPerValue(moneyValue) { 
                this.updateMoneyDetailsAmount();
                return (this.state.moneyDetails[moneyValue] || 0) * moneyValue;
            }

           handleInputChange(ev, moneyValue) {
                let value = ev.target.value;
                
                // Remove leading zeros but preserve "0." for decimals
                if (value.length > 1 && value[0] === '0' && value[1] !== '.') {
                    value = value.replace(/^0+/, '');
                    if (value === '') value = '0';
                    ev.target.value = value;
                }
                
                // Update state
                this.state.moneyDetails[moneyValue] = value;
            }

            handleInputFocus(ev, moneyValue) {
                // Remove "0" when focused
                if (ev.target.value === '0') {
                    ev.target.value = '';
                }
            }

            handleInputBlur(ev, moneyValue) {
                let value = ev.target.value;
                
                // If blank or zero, set to "0"
                if (value === '' || value === '0' || parseFloat(value) === 0) {
                    value = '0';
                    ev.target.value = value;
                }
                
                // Update state
                this.state.moneyDetails[moneyValue] = value;
            }

        }        

    Registries.Component.extend(MoneyDetailsgPopup, MoneyDetailsgPopupCashOpeningZero);
    return MoneyDetailsgPopupCashOpeningZero;

});