/** @odoo-module **/

import ProductsWidget from 'point_of_sale.ProductsWidget';
import Registries from 'point_of_sale.Registries';

export const ShopOnProductWidget = (ProductsWidget) =>
    class ShopOnProductWidget extends ProductsWidget {
        get productsToDisplay() {
            var self = this;
            var res = super.productsToDisplay
            var products = []
            var tmpl_ids = []
            if (this.searchWord !== '') {
                if (self.env.pos.config.setu_pos_enable_product_variants) {
                    _.each(res, function (each_product, i) {
                        if (each_product.attribute_line_ids.length > 0) {
                            if (!tmpl_ids.includes(each_product.product_tmpl_id)) {
                                products.push(each_product)
                            }
                            tmpl_ids.push(each_product.product_tmpl_id)
                        } else {
                            products.push(each_product)
                        }

                    })
                    return products
                }
            } else {
                if (self.env.pos.config.setu_pos_enable_product_variants) {
                    _.each(self.env.pos.db.product_by_category_id[self.selectedCategoryId], function (product_id, i) {
                        var each_product = self.env.pos.db.product_by_id[product_id]
                        if (each_product.attribute_line_ids.length > 0) {
                            if (!tmpl_ids.includes(each_product.product_tmpl_id)) {
                                products.push(each_product)
                            }
                            tmpl_ids.push(each_product.product_tmpl_id)
                        } else {
                            products.push(each_product)
                        }

                    })
                    return products
                }
            }
            return res
        }
         _switchCategory(event) {
            setTimeout(()=> {
                $('.rightpane-header').scrollTo($('.categories-header'))
            }, 100);
            super._switchCategory(event);
        }
    };

Registries.Component.extend(ProductsWidget, ShopOnProductWidget);
