odoo.define("sh_pos_theme_responsive.ticket_screen", function (require) {
    "use strict";
    
    const Registries = require("point_of_sale.Registries");
    const TicketScreen = require("point_of_sale.TicketScreen");
    
    const PosTicketScreen = (TicketScreen) =>
    class extends TicketScreen {
    	constructor() {
            super(...arguments);            
        }
    	mounted() {
    		if(this.env.isMobile){
            	$('.pos-content').addClass('sh_client_pos_content')
            	$('.sh_product_management').addClass('hide_cart_screen_show')
            	$('.sh_cart_management').addClass('hide_product_screen_show')
            }
    	}
    };

    Registries.Component.extend(TicketScreen, PosTicketScreen);
    
});