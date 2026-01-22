odoo.define("shopon_pos_theme.TicketScreen", function (require) {
  "use strict";
  const TicketScreen = require("point_of_sale.TicketScreen");
  const Registries = require("point_of_sale.Registries");

  const ShopOnTicketScreen = (TicketScreen) =>
    class extends TicketScreen {
        _openSideBar(){
            $('.dn_sidebar').toggle(100)
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
        _toggleSideBar(){
            $('.dn_sidebar').toggle(100)
        }
    };
  Registries.Component.extend(TicketScreen, ShopOnTicketScreen);
});