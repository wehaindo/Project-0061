odoo.define("shopon_pos_theme.ProductItem", function (require) {
    "use strict";

    const ProductItem = require("point_of_sale.ProductItem");
    const Registries = require('point_of_sale.Registries');
    const { useRef, onPatched, onMounted, useState } = owl;

    const ShopOnProductItem = (ProductItem) =>
        class extends ProductItem {
            setup() {
                super.setup()
                onMounted(() => {
                    var self = this;                    
                });

            }
            async onProductInfoClickSetu() {
                event.stopPropagation();
                return super.onProductInfoClick();
            }
        }

    Registries.Component.extend(ProductItem, ShopOnProductItem)

});
