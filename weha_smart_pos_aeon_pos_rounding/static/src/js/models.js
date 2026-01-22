odoo.define("weha_smart_pos_aeon_pos_rounding.models", function(require){
    'use strict';
    
    var {  Order } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    var utils = require('web.utils');


    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;
    const Markup = utils.Markup


    const RoundingOrder = (Order) =>
    class extends Order {

        constructor(obj, options) {
            super(obj, options);            
        }

        get_rounding_applied() {
            if(this.pos.config.cash_rounding && this.is_refund) {
                const only_cash = this.pos.config.only_round_cash_method;
                const paymentlines = this.get_paymentlines();
                const last_line = paymentlines ? paymentlines[paymentlines.length-1]: false;
                const last_line_is_cash = last_line ? last_line.payment_method.is_cash_count == true: false;
                if (!only_cash || (only_cash && last_line_is_cash)) {
                    return 0;
                }
                else {
                    return 0;
                }
            }else{
                return super.get_rounding_applied();
            }            
        }

        // get_total_without_tax() {
        //     console.log('this.pos.currency.rounding');
        //     console.log(this.pos.currency.rounding);
        //     var total_without_tax =  round_pr(this.orderlines.reduce((function(sum, orderLine) {
        //         return sum + orderLine.get_price_without_tax();
        //     }), 0), this.pos.currency.rounding);
        //     console.log('total_without_tax');
        //     console.log(total_without_tax);
        //     return total_without_tax;
        // }

        // get_total_tax() {
        //     if (this.pos.company.tax_calculation_rounding_method === "round_globally") {
        //         // As always, we need:
        //         // 1. For each tax, sum their amount across all order lines
        //         // 2. Round that result
        //         // 3. Sum all those rounded amounts
        //         var groupTaxes = {};
        //         this.orderlines.forEach(function (line) {
        //             var taxDetails = line.get_tax_details();
        //             var taxIds = Object.keys(taxDetails);
        //             for (var t = 0; t<taxIds.length; t++) {
        //                 var taxId = taxIds[t];
        //                 if (!(taxId in groupTaxes)) {
        //                     groupTaxes[taxId] = 0;
        //                 }
        //                 groupTaxes[taxId] += taxDetails[taxId];
        //             }
        //         });
    
        //         var sum = 0;
        //         var taxIds = Object.keys(groupTaxes);
        //         for (var j = 0; j<taxIds.length; j++) {
        //             var taxAmount = groupTaxes[taxIds[j]];
        //             sum += round_pr(taxAmount, this.pos.currency.rounding);
        //         }
        //         console.log("round_globally")
        //         console.log(sum)
        //         return Math.floor(sum);
        //     } else {
        //         var sum =  round_pr(this.orderlines.reduce((function(sum, orderLine) {                    
        //             return sum + orderLine.get_tax();                    
        //         }), 0), this.pos.currency.rounding);
        //         console.log("not round_globally")
        //         console.log(sum)
        //         return Math.floor(sum);
        //     }
        // }
    }

    
    Registries.Model.extend(Order, RoundingOrder);

    
})