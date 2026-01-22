odoo.define('weha_smart_pos_aeon_sku.ProductScreen', function(require) {
    'use strict';

    
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');

    const AeonSkuProductScreen = (ProductScreen) =>
        class extends ProductScreen {

            setup() {
                super.setup();
                console.log("AeonSkuProductScreen");
            }

            async _barcodeProductAction(code) {
                console.log("AeonSkuProductScreen");
                console.log("_barcodeProductAction");            
                const product = this.db.get_product_by_barcode(code.base_code);
                const order = this.env.pos.get_order();
                // if (!order) {
                //     return;
                // }
                console.log(order.numpadBuffer);                
                await super._barcodeProductAction(code);
            }
                        
        }

    Registries.Component.extend(ProductScreen, AeonSkuProductScreen);

    // return ProductScreen;
});