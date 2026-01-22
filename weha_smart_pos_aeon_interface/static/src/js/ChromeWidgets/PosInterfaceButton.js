odoo.define('weha_smart_pos_aeon_interace.PosInterfaceButton', function(require){
    'use strict';
    
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class PosInterfaceButton extends PosComponent {
        setup(){
            super.setup();
        }
        
        async onClick() {
            console.log("Clicked");
            var data = {
                type: "pool",
                raw: "Total 10000"
            }
            this.trigger('send-pos-interface', { data });
            // this.env.sendMessage(data);
        }
    }

    PosInterfaceButton.template = 'PosInterfaceButton';

    Registries.Component.add(PosInterfaceButton);

    return PosInterfaceButton;

});