odoo.define('weha_smart_pos_aeon_price_base.ProductInfoPopup', function (require) {
    "use strict";

    const ProductInfoPopup  = require('point_of_sale.ProductInfoPopup');
    const Registries = require('point_of_sale.Registries');

    
    const PriceBaseProductInfoPopup = (ProductInfoPopup) => 
        class extends ProductInfoPopup {

            setup() {
                super.setup();             
            }
    
            _hasMarginsCostsAccessRights() {
                return false
            }
        }

    Registries.Component.extend(ProductInfoPopup, PriceBaseProductInfoPopup);

})