odoo.define('weha_smart_pos_aeon_pos_data.ProductScreen', function(require) {
    'use strict';
    
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');

    const PosDataProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            setup() {
                super.setup();
            }                      
        } 

    Registries.Component.extend(ProductScreen, PosDataProductScreen);
    return ProductScreen;
})

