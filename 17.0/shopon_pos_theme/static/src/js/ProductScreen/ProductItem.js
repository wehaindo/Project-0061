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
                    if (self.env.pos.config.setu_pos_enable_product_variants) {
                        var product = this.props.product
                        var variants = self.env.pos.db.has_variant(product.product_tmpl_id)
                        if(variants){
                            _.each(variants, function(each_variant){

                                if(each_variant.product_template_attribute_value_ids && each_variant.product_tmpl_id){
                                    if(self.env.pos.db.product_attr && !self.env.pos.db.product_attr[each_variant.product_tmpl_id]){
                                        self.env.pos.db.product_attr[product.product_tmpl_id] = []
                                    }
                                    _.each(each_variant.product_template_attribute_value_ids, function(each_value){
                                        if(!self.env.pos.db.product_attr[product.product_tmpl_id].includes(each_value)){
                                            self.env.pos.db.product_attr[product.product_tmpl_id].push(each_value)
                                        }
                                    });
                                }
                            });
                        }
                        _.each($('.product'), function (each) {
                            if (product.id == each.dataset.productId && variants) {
                                if (variants.length > 1) {
                                    $(each).find('.price-tag').addClass('setu_has_variant');
                                    $(each).find('.price-tag').text(variants.length + ' variants');
                                }
                            }
                        })
                    }
                });

            }
            async onProductInfoClickSetu() {
                event.stopPropagation();
                return super.onProductInfoClick();
            }
        }

    Registries.Component.extend(ProductItem, ShopOnProductItem)

});
