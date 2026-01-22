odoo.define("setu_pos_theme.Chrome", function (require) {
    "use strict";

    const Chrome = require("point_of_sale.Chrome");
    const Registries = require('point_of_sale.Registries');

    const SetuChrome = (Chrome) =>
        class extends Chrome {
           get isHeaderScreenShown() {
                if(this.env.pos.config){
                    return this.env.pos.config.module_pos_restaurant ? 'FloorScreen' : 'ShopScreen';
                }
                else{
                    return 'ShopScreen'
                }
           }
        }

    Registries.Component.extend(Chrome, SetuChrome)

});
