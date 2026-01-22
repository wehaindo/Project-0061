odoo.define('weha_smart_pos_aeon_pos_data.ProductScreen', function(require) {
    'use strict';
    
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');

    const PosDataProductScreen = (ProductScreen) =>
        class extends ProductScreen {

            setup() {
                super.setup();
            }

            
            // async _barcodeProductAction(code) {
            //     console.log("_barcodeProductAction");
            //     var newBarcode = code.base_code;
            //     var finalBarcode = newBarcode.padEnd(18,'0');
            //     code.base_code = finalBarcode;
            //     console.log("_barcodeProductAction");
            //     console.log(finalBarcode);
            //     console.log(code.base_code);
            //     super._barcodeProductAction(code);
            // }

            // async _barcodeProductAction(code) {                
            //     console.log("_barcodeProductAction");
            //     super._barcodeProductAction(code);
                // // Get Product By Barcode                
                // let product = await this.env.pos.get_product_by_barcode(code.base_code);
                // if (!product) {
                //     // find the barcode in the backend
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
                // const options = await this._getAddProductOptions(product, code);
                // // Do not proceed on adding the product when no options is returned.
                // // This is consistent with _clickProduct.
                // if (!options) return;
            
                // // update the options depending on the type of the scanned code
                // if (code.type === 'price') {
                //     Object.assign(options, {
                //         price: code.value,
                //         extras: {
                //             price_manually_set: true,
                //         },
                //     });
                // } else if (code.type === 'weight') {
                //     Object.assign(options, {
                //         quantity: code.value,
                //         merge: false,
                //     });
                // } else if (code.type === 'discount') {
                //     Object.assign(options, {
                //         discount: code.value,
                //         merge: false,
                //     });
                // }
                // this.currentOrder.add_product(product,  options);
                // NumberBuffer.reset();
            // }
        } 

    Registries.Component.extend(ProductScreen, PosDataProductScreen);
    return ProductScreen;
})

