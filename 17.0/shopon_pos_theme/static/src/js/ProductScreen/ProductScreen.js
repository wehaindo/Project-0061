odoo.define("shopon_pos_theme.ProductScreen", function (require) {
  "use strict";
  const ProductScreen = require("point_of_sale.ProductScreen");
  const Registries = require("point_of_sale.Registries");

  const ShopOnProductScreen = (ProductScreen) =>
    class extends ProductScreen {
        onMounted() {
            super.onMounted();
            this.env.pos.set_stock_qtys(this.env.pos.setu_product_qtys);
            this.env.pos.setu_change_qty_css();
        }
        NumpadVisibility() {
            $('.numpad').slideToggle('slow', function() {

                if($('.NumpadVisibility').find('span').hasClass('hd_numpad'))
                {
                    $('.NumpadVisibility').find('span').text("Hide Numpad")
                    $('.NumpadVisibility').find('span').removeClass('hd_numpad').addClass('dh_numpad');
                }
                else{
                    $('.NumpadVisibility').find('span').text("Show Numpad")
                    $('.NumpadVisibility').find('span').removeClass('dh_numpad').addClass('hd_numpad');
                }
            });
        }
        _openSideBar(){
            $('.dn_sidebar').show(100)
            $('.open_side_bar_menu').addClass('toggleSidebarMenu')
            if(this.env.isMobile){
                $('.rightpane').addClass('d-none')
                $('.leftpane').addClass('d-none')
                $('.dn_sidebar').addClass('full_dn_sidebar')
            }
        }
        _closeSideBar(){
            $('.dn_sidebar').hide(100)
            $('.open_side_bar_menu').removeClass('toggleSidebarMenu')
            if(this.env.isMobile){
                $('.rightpane').removeClass('d-none')
                $('.leftpane').removeClass('d-none')
                $('.dn_sidebar').removeClass('full_dn_sidebar')
            }
        }
        async onClosePOS() {
            try {
                const info = await this.env.pos.getClosePosInfo();
                this.showPopup('ClosePosPopup', { info: info, keepBehind: true });
            } catch (e) {
                if (identifyError(e) instanceof ConnectionAbortedError||ConnectionLostError) {
                    this.showPopup('OfflineErrorPopup', {
                        title: this.env._t('Network Error'),
                        body: this.env._t('Please check your internet connection and try again.'),
                    });
                } else {
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Unknown Error'),
                        body: this.env._t('An unknown error prevents us from getting closing information.'),
                    });
                }
            }
        }
        async _clickProduct(event) {
            var self = this;
            this.product_variants = []
            this.alternative_products = []
            var alternative_ids = []
            _.each(self.env.pos.db.product_by_id, function (each_product) {
                if (each_product.product_tmpl_id == event.detail.product_tmpl_id) {
                    self.product_variants.push(each_product)
                    if (each_product.setu_alternative_products.length > 0) {
                        _.each(each_product.setu_alternative_products, function (each) {
                            var product = self.env.pos.db.get_product_by_id(each)
                            if (!alternative_ids.includes(each)) {
                                if (self.env.pos.config.setu_pos_display_alternative_products) {
                                    self.alternative_products.push(product)
                                }
                            }
                            alternative_ids.push(each)
                        })
                    }
                }
            })
            if (this.product_variants.length > 1) {
                if (!self.env.pos.config.setu_pos_variants_group_by_attribute && self.env.pos.config.setu_pos_enable_product_variants) {
                    if (this.product_variants.length > 6 && this.product_variants.length < 15) {
                        self.showPopup("ShopOnVariantPopup", { 'title': 'Product Variants', 'morevariant_class': 'setu_lessthan_8_variants', product_variants: this.product_variants, alternative_products: this.alternative_products })
                    }
                    else if (this.product_variants.length > 15) {
                        self.showPopup("ShopOnVariantPopup", { 'title': 'Product Variants', 'morevariant_class': ' setu_morethan_15_variants', product_variants: this.product_variants, alternative_products: this.alternative_products })
                    }
                    else {
                        self.showPopup("ShopOnVariantPopup", { 'title': 'Product Variants', product_variants: this.product_variants, alternative_products: this.alternative_products })
                    }

                }
                else if (self.env.pos.config.setu_pos_variants_group_by_attribute && self.env.pos.config.setu_pos_enable_product_variants) {
                    self.Attribute_names = []
                    _.each(event.detail.attribute_line_ids, function (each_attribute) {
                        self.Attribute_names.push(self.env.pos.db.product_temlate_attribute_line_by_id[each_attribute])
                    })
                    if (this.Attribute_names.length > 0) {
                        self.showPopup("ShopOnVariantPopup", { 'title': 'Product Variants', attributes_name: this.Attribute_names, alternative_products: this.alternative_products, product_tmpl_id:event.detail.product_tmpl_id })
                    } else {
                        super._clickProduct(event)
                    }
                }
                else {

                    super._clickProduct(event)
                }

            }else{
                if (this.alternative_products.length > 0 && self.env.pos.config.setu_pos_display_alternative_products && self.env.pos.config.setu_pos_variants_group_by_attribute) {
                    self.showPopup("ShopOnVariantPopup", { 'title': 'Alternative Product', attributes_name: [], alternative_products: this.alternative_products })
                }
                if(this.alternative_products.length > 0 && self.env.pos.config.setu_pos_display_alternative_products && !self.env.pos.config.setu_pos_variants_group_by_attribute){
                    self.showPopup("ShopOnVariantPopup", { 'title': 'Alternative Product', product_variants: [], alternative_products: this.alternative_products })
                }
                super._clickProduct(event)
            }
        }
    };
  Registries.Component.extend(ProductScreen, ShopOnProductScreen);
});