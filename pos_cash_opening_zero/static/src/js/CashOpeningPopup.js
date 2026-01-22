odoo.define('pos_cash_opening_zero.CashOpeningPopup', function (require) {
    "use strict";    
    const { useState, useRef, onMounted } = owl;
    const CashOpeningPopup = require('point_of_sale.CashOpeningPopup');
    const Registries = require("point_of_sale.Registries")

    const CashOpeningZero = (CashOpeningPopup) =>
        class extends CashOpeningPopup{
            setup() {
                super.setup();
                this.manualInputCashCount = null;
                this.state.openingCash = 0;
                this.state.displayMoneyDetailsPopup= false;
                // this.state = useState({
                //     notes: "",
                //     openingCash: 0,
                //     displayMoneyDetailsPopup: false,
                // });
                onMounted(() => {
                    var openingCashInputRef = useRef('openingCashInput');
                    console.log("openingCashInputRef");
                    // console.log(openingCashInputRef);
                    // this.openingCashInputRef.el.value = this.state.openingCash;
                });
            }

            openDetailsPopup() {                                
                this.state.displayMoneyDetailsPopup = true;
            }

            closeDetailsPopup() {
                this.state.displayMoneyDetailsPopup = false;
            }
        };
    CashOpeningZero.template = 'pos_cash_opening_zero.CashOpeningPopup';
    Registries.Component.extend(CashOpeningPopup, CashOpeningZero);
    return CashOpeningZero
});