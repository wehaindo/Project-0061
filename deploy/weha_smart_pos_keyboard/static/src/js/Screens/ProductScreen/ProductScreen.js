
/** @odoo-module **/

import ProductScreen from 'point_of_sale.ProductScreen';
import Registries from 'point_of_sale.Registries';
// import KioskBoard from 'kioskboard';

export const KeyboardProductScreen = (ProductScreen) => 
    class extends ProductScreen {
        setup() {
            super.setup();
        }            

    };
        

Registries.Component.extend(ProductScreen, KeyboardProductScreen)
