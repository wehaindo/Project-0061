odoo.define("shopon_pos_theme.MobileOrderWidget", function (require) {
  "use strict";
  const MobileOrderWidget = require("point_of_sale.MobileOrderWidget");
  const Registries = require("point_of_sale.Registries");

  const ShopOnMobileOrderWidget = (MobileOrderWidget) =>
    class extends MobileOrderWidget {
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
  Registries.Component.extend(MobileOrderWidget, ShopOnMobileOrderWidget);
});