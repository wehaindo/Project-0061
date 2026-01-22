odoo.define('weha_smart_pos_aeon_customer_display.PosEnableDisplayButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    const { useState } = owl;

    class PosEnableDisplayButton extends PosComponent {
        setup() {
            super.setup();            
            var isPosOpen = false;
        }
        onClick() {
            console.log('Send Open Close Customer Display');
            var self = this;
            this.isPosOpen = !this.isPosOpen
            // var pos_interface_conn = new WebSocket('ws://localhost:1338');   
            // console.log("Connnect to Customer Display 1338");
            const pos = this.env.pos;
            console.log(pos);
            var order = pos.get_order();        
            var pos_session = pos.pos_session;
            var data = {
                actionType: 'openOrderUi',
                message :{        
                    is_pos_open: this.isPosOpen,
                    pos_store_name: pos.config.res_branch_id[1],
                    pos_cashier_name: pos.pos_session.config_id[1]
                }
            }
            // pos_interface_conn.addEventListener("open", (event) => {
            //     pos_interface_conn.send(JSON.stringify(data));
            //     pos_interface_conn.close();
            // });
            fetch("http://localhost:8001/customerdisplay", {
                method: "POST",
                body: JSON.stringify(data),
                headers: {
                  "Content-type": "application/json; charset=UTF-8"
                }
            }).catch((error) => {
                console.log(error);
            });
        }
    }
    
    PosEnableDisplayButton.template = 'PosEnableDisplayButton';
    Registries.Component.add(PosEnableDisplayButton);
    return PosEnableDisplayButton;

});