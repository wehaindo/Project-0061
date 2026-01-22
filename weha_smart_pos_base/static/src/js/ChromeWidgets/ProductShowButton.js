odoo.define('weha_smart_pos_base.ProductShowButton', function(require){
    'use strict';
    
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class ProductShowButton extends PosComponent {
        setup(){
            super.setup();
        }
        
        async onClick() {
            this.env.pos.config.is_show_product_grid = !this.env.pos.config.is_show_product_grid;
        }
    }

    ProductShowButton.template = 'ProductShowButton';

    Registries.Component.add(ProductShowButton);

    return ProductShowButton;

});