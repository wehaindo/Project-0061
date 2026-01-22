odoo.define('weha_smart_pos_aeon_discount.DB', function(require){
    'use strict'

    var PosDB = require('point_of_sale.DB');

    PosDB.include({       
        is_rtc: function(barcode){
            rtcDigit = barcode.substring(13,17)
            discount = parseInt(rtcDigit)
            if (discount > 0){
                return true
            }
            return false
        },
        
        check_digit: function(barcode){
            let array = barcode.split('').reverse();

            let total = 0;
            let i = 1;
            array.forEach(number => {
                number = parseInt(number);
                if (i % 2 === 0) {
                    total = total + number;
                }
                else
                {
                    total = total + (number * 3);
                }
                i++;
            });
            return (Math.ceil(total / 10) * 10) - total;
        },
        get_product_by_barcode: function(barcode){   
            console.log("barcode");
            console.log(barcode);
            if (barcode.length == 12){
                var digit = this.check_digit(barcode);
                barcode = barcode + digit.toString();
                console.log(barcode);
                if(this.product_by_barcode[barcode]){
                    return this.product_by_barcode[barcode];
                }
            }      
            else if(this.product_by_barcode[barcode]){
                return this.product_by_barcode[barcode];
            } else if (this.product_packaging_by_barcode[barcode]) {
                return this.product_by_id[this.product_packaging_by_barcode[barcode].product_id[0]];
            }

            return undefined;
        }
    });
});