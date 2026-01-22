odoo.define("shopon_pos_theme.ProductScreen", function (require) {
  "use strict";
  const ProductScreen = require("point_of_sale.ProductScreen");
  const Registries = require("point_of_sale.Registries");

  const ShopOnProductScreen = (ProductScreen) =>
    class extends ProductScreen {
        onMounted() {
            super.onMounted(() => this.NumpadVisibility());
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
        
    };
  Registries.Component.extend(ProductScreen, ShopOnProductScreen);
});