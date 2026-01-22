/** @odoo-module **/

import ProductsWidget from 'point_of_sale.ProductsWidget';
import Registries from 'point_of_sale.Registries';

export const ShopOnProductWidget = (ProductsWidget) =>
    class ShopOnProductWidget extends ProductsWidget {        
        _switchCategory(event) {
            setTimeout(()=> {
                $('.rightpane-header').scrollTo($('.categories-header'))
            }, 100);
            super._switchCategory(event);
        }
    };

Registries.Component.extend(ProductsWidget, ShopOnProductWidget);
