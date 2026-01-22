odoo.define('weha_smart_pos_aeon_discount.ProductScreen', function (require) {
    "use strict";
    const ProductScreen = require('weha_smart_pos_aeon_multi_uom');
    const Registries = require('point_of_sale.Registries');
    var utils = require('web.utils');
    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;
    
    const AeonDiscountProductScreen = (ProductScreen) =>
    class extends ProductScreen {

        checkDigitRtc(input) {
            let array = input.split('').reverse();
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
        }

        getRtcDiscount(barcode){
            console.log('getRtcDiscount');
            var discount = 0;
            if(barcode.length == 19){
                var lastDigit = barcode.substring(14,19);
                var discount = parseInt(lastDigit);
            }else if (barcode.length == 18){            
                var lastDigit = barcode.substring(13,17);
                var discount = parseInt(lastDigit);    
            }
            return discount;
        }

        isRtc(barcode){
            console.log('isRtc');
            var discount = this.getRtcDiscount(barcode)
            if (discount > 0){
                console.log('RTC Detected');                
                // if(barcode.length == 19){
                //     // 2000081960338100050
                //     return true;
                // }else{
                //     // 200008196033000509
                //     var checkdigit = this.checkDigitRtc(barcode.substring(0,17));
                //     console.log(checkdigit);
                //     console.log(barcode[17]);
                //     if(barcode[17] == checkdigit.toString()){
                //         console.log('Discount larger than 0');
                //         return true
                //     }else{
                //         console.log('Check Digit not valid');
                //         return false;
                //     }
                // }
                return true;                                
            }
            console.log('Return False');
            return false;
        }

        // 200009115736000509
        async _barcodeProductAction(code) {
            console.log("Aeon Discount _barcodeProductAction");
            if(this.isRtc(code.base_code)){
                code.type = "discount";
                code.value = this.getRtcDiscount(code.base_code);               
                var newBarcode = code.base_code.substring(0,12)
                newBarcode = newBarcode + this.checkDigitRtc(newBarcode)
                console.log(newBarcode);
                var finalBarcode = newBarcode.padEnd(18,'0');
                console.log(finalBarcode);
                code.base_code = finalBarcode;
                const product = this.env.pos.db.get_product_by_barcode(finalBarcode)
                if (!product) {
                    return;
                }
                // if (!product) {
                //     console.log("Product not found")
                //     let foundProductIds = [];
                //     try {
                //         foundProductIds = await this.rpc({
                //             model: 'product.product',
                //             method: 'search',
                //             args: [[['barcode', '=', code.base_code]]],
                //             context: this.env.session.user_context,
                //         });
                //     } catch (error) {
                //         if (isConnectionError(error)) {
                //             return this.showPopup('OfflineErrorPopup', {
                //                 title: this.env._t('Network Error'),
                //                 body: this.env._t("Product is not loaded. Tried loading the product from the server but there is a network error."),
                //             });
                //         } else {
                //             throw error;
                //         }
                //     }
                //     if (foundProductIds.length) {
                //         await this.env.pos._addProducts(foundProductIds);
                //         // assume that the result is unique.
                //         product = this.env.pos.db.get_product_by_id(foundProductIds[0]);
                //     } else {
                //         return this._barcodeErrorAction(code);
                //     }
                // }
                console.log("Product found")
                const options = await this._getAddProductOptions(product);
                // Do not proceed on adding the product when no options is returned.
                // This is consistent with _clickProduct.
                if (!options) return;

                // update the options depending on the type of the scanned code
                if (code.type === 'price') {
                    Object.assign(options, { price: code.value });
                } else if (code.type === 'weight') {
                    Object.assign(options, {
                        quantity: code.value,
                        merge: false,
                    });
                } else if (code.type === 'discount') {
                    Object.assign(options, {
                        discount: code.value,
                        merge: false,
                    });
                }
                this.currentOrder.add_product(product,  options)
                var line = this.currentOrder.get_last_orderline();
                line.price_manually_set = true;
                // line.set_discount(this.getRtcDiscount(code.base_code));
                line.set_discount_type('rtc');
            }else{
                console.log("Not RTC")
                await super._barcodeProductAction(code);
            }                                                             
        }
    };

    Registries.Component.extend(ProductScreen, AeonDiscountProductScreen);
    
});